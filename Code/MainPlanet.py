from Code.Planet import Planet
from math import ceil


class MainPlanet(Planet):
    """The class that keeps all the info about the organism and is more detailed than Planet."""
    TECH_CAP = 15
    ENGINEERING_CAP = 30

    def __init__(self, planet):
        # copy-constructor for planet
        self.planet_name = planet.planet_name
        self.landmass = planet.landmass
        self.distance = planet.distance
        self.is_gz = planet.is_gz
        self.atmosphere = planet.atmosphere
        self.radius = planet.radius

        self.total_population = 100000
        self.prev_population = self.total_population
        self.population_health = 100
        self.tech_counter = 5
        self.tech_focus = None
        self.tech_list = [0, 0, 0, 0]
        # self.tech_medicine -> tech_list[0]
        # self.tech_agriculture -> tech_list[1]
        # self.tech_architecture -> tech_list[2]
        # self.tech_engineering -> tech_list[3]
        self.atmosphere_multiplier = 1
        self.landmass_multiplier = 1
        self.population_multiplier = 1
        self.usable_landmass = self.calc_usable_landmass()
        self.calculated_atmosphere = self.atmosphere * self.atmosphere_multiplier
        self.calculated_temperature = self.calc_temperature()
        self.life_quality = self.calc_life_quality()
        self.progression = 0

    def spend_points(self, points):  # return value form GUI
        """Spend the technology points in the beginning of the simulation."""
        self.tech_list[0] = points[0]
        self.tech_list[1] = points[1]
        self.tech_list[2] = points[2]
        self.tech_list[3] = 0

    def set_research_focus(self, index):
        """Method to choose focus to upgrade technologies."""
        if self.tech_focus != index:
            self.tech_counter = 5
            self.tech_focus = index

    def update_research_focus(self):
        """Check if research is complete, and the focus needs to be chosen again."""
        if self.tech_counter == 1:
            if self.tech_focus is not None:
                self.update_technologies(self.tech_focus)
                self.tech_counter = 5
        else:
            if self.tech_focus is not None:
                self.tech_counter -= 1

    def change_base_values(self, event):
        """Choose the type of method to call, depending on the type of event."""
        if event.type_event == 0:
            self.update_multipliers(event.get_multipliers())
        if event.type_event == 1:
            self.update_technologies(event.tech_index)

    def update_multipliers(self, multipliers):
        """After a disaster, update the multipliers."""
        self.atmosphere_multiplier *= multipliers[0]
        self.landmass_multiplier *= multipliers[1]
        self.population_health *= multipliers[2]
        self.population_multiplier = multipliers[3]

    def update_technologies(self, tech_index):
        """When a breakthrough has appeared, it updates the right technology."""
        if tech_index != 3 and self.tech_list[tech_index] < self.TECH_CAP:
            self.tech_list[tech_index] += 1
        elif tech_index == 3 and self.tech_list[tech_index] < self.ENGINEERING_CAP:
            self.tech_list[tech_index] += 1

    def update_variables(self):
        """Update all variables separately, through its correct methods."""
        # atmosphere
        self.calculated_atmosphere = self.calc_atmosphere()
        # temperature
        self.calculated_temperature = self.calc_temperature()
        # usable landmass
        self.usable_landmass = self.calc_usable_landmass()
        # population health
        if self.population_health + self.tech_list[0] >= 100:
            self.population_health = 100
        else:
            self.population_health += self.tech_list[0]
        # life quality
        self.calc_life_quality()
        # total population
        self.calc_total_population()
        # progression
        self.progression = self.calc_progression()
        self.update_research_focus()

    def calc_atmosphere(self):
        """Calculate the atmosphere, and regenerate the multiplier."""
        if self.atmosphere_multiplier + self.tech_list[1] / 150 >= 1:
            self.atmosphere_multiplier = 1
        else:
            self.atmosphere_multiplier += self.tech_list[1] / 150
        return self.atmosphere * self.atmosphere_multiplier

    def calc_temperature(self):  # goldi -25 - +50 # -250 - +500
        """Calculate the temperature depending on the atmosphere and distance."""
        if self.distance < self.GOLDILOCK_DISTANCE:
            const = -1.0
        else:
            const = 0.5
        return (250 - (self.distance / 600000)) * (100 / self.atmosphere) if self.is_gz else 230 \
                                                                                             + 3.5 / const - const * (
            -const * self.calculated_atmosphere + 300 + (const * self.distance / 1_000_000) * 4)

    def calc_usable_landmass(self):
        """Calculate the usable landmass, depending on archeology and agriculture, and its multiplier."""
        from math import ceil
        tech_variable = (self.tech_list[2] * 0.5 + self.tech_list[1] * 0.5) / self.TECH_CAP
        if self.landmass_multiplier < 1:
            if self.landmass_multiplier + tech_variable / 10 >= 1:
                self.landmass_multiplier = 1
            else:
                self.landmass_multiplier += tech_variable / 10
        usable_landmass = ceil(self.landmass_multiplier * self.landmass * (tech_variable * 0.8 + 0.2))
        return usable_landmass

    def calc_life_quality(self):
        """Calculate the life quality, depending on the temperature,landmass, engineering, and population health."""
        if (self.calculated_temperature > -25) and (self.calculated_temperature < 50):
            x = -(self.calculated_temperature + 25) * (
                self.calculated_temperature - 50) / 1406.25  # / number between -a and 0
            self.life_quality = ceil(((self.tech_list[3] / 6) + ((self.usable_landmass / self.landmass) * 35) + (
                ((1 - x) * self.tech_list[2] / self.TECH_CAP + x) * 20) + (self.population_health * 0.4)) * 100) / 100
        else:
            self.life_quality = ceil(((self.tech_list[3] / 6) + ((self.usable_landmass / self.landmass) * 35) + (
                ((1 * self.tech_list[2] / self.TECH_CAP) * 20) + (self.population_health * 0.4))) * 100) / 100
            if self.calculated_temperature <= -25:
                self.life_quality *= 1 - (self.calculated_temperature + 25) / (
                    -248)  # the lower the temperature, the worse the life quality
            else:
                self.life_quality *= 1 - (self.calculated_temperature - 50) / (
                    500)  # the higher the temperature, the worse the life quality
        return self.life_quality

    def calc_total_population(self):
        """Calculate the total population, depending on life quality, and its current population."""
        if self.total_population < 5000:
            self.total_population = int(
                self.total_population + ((self.life_quality / 100) - 0.5) * 3 * self.total_population)
        elif self.total_population > 1000000000:
            self.total_population = int(
                self.total_population + ((self.life_quality / 100) - 0.5) * 1000000000 / 1.3)
        else:
            self.total_population = int(
                self.total_population + ((self.life_quality / 100) - 0.5) * self.total_population / 1.3)
        self.total_population *= self.population_multiplier
        self.population_multiplier = 1
        if self.total_population < 0:
            self.total_population = 0

    def calc_progression(self):
        """Calculate the progression, depending on the population, and the life quality, and a few technologies."""
        population = int(self.total_population)
        if self.prev_population - population >= 0:
            progression = self.progression - (1 - (self.life_quality / 100)) * (
                (self.prev_population - population) / 250000)
            if progression < (self.progression / 1.5):
                progression = self.progression / 1.5
        else:
            if self.total_population >= 1000000:
                population = 1000000
            progression = self.progression + (self.tech_list[3] * 1 + self.tech_list[2] * 0.25 + self.tech_list[
                0] * 0.1 + ((self.life_quality / 100) - 0.5) * 10) * (population / 500000)
        if progression < 0:
            progression = 0
        if progression > 1000:
            progression = 1000
        return progression

    def show_information(self):
        """Print the information about the planet, like distance, name of planet, and more relevant information."""
        return {"Turns left for chosen technology:": self.tech_counter, "Name of Planet:": self.planet_name,
                "Distance (kilometer):": ceil(self.distance),
                "Radius (kilometer):": ceil(self.radius),
                "Temperature (°C):": ceil(self.calculated_temperature),
                "Usable Landmass (%):": round(self.usable_landmass, 2),
                "Atmosphere (%):": round(self.calculated_atmosphere, 2),
                "Health (%):": round(self.population_health, 2),
                "Life Quality (%):": round(self.life_quality, 2), "Population:": ceil(self.total_population),
                "Medicine:": str(self.tech_list[0]) + "/15", "Agriculture:": str(self.tech_list[1]) + "/15",
                "Architecture:": str(self.tech_list[2]) + "/15", "Engineering:": str(self.tech_list[3]) + "/30"}

    def cache_population(self):
        """Save the population, to calculate the difference in the next turn."""
        self.prev_population = int(self.total_population)

    def __repr__(self):
        return str(self.show_information())

    def __str__(self):
        return self.__repr__()



        # m = MainPlanet(150000000)
        # print(m.life_quality)
        # m.tech_agriculture = 4
        # m.tech_architecture = 4
        # m.tech_engineering = 7
        # m.tech_medicine = 3
        # for x in ranhe(0,100):
        #     m.update_variables()
        #     print(m.life_quality,m.usable_landmass)
