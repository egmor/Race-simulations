from random import *

class Driver:
    def __init__(self, name, power, tire_type, speed, experience, fuel_management, pit_stop_quality, fuel_weight):
        self.name = name
        self.power = power
        self.tire_type = tire_type
        self.speed = speed
        self.experience = experience
        self.fuel_management = fuel_management
        self.pit_stop_quality = pit_stop_quality

        self.tire_lap = 0
        self.total_time = 0.0
        self.tire_wear = 100.0

        self.fuel_weight = fuel_weight
        self.is_active = True

    def make_pitstop(self, lap, new_tire_type):
        self.tire_type = new_tire_type
        self.tire_lap = 0
        self.tire_wear = 100.0
        tire_change_time = 3.0 - self.pit_stop_quality / 100.0
        self.total_time += 20.0 + tire_change_time
        print(f"[{lap}] {self.name} заехал на пит-стоп и переобулся в {self.tire_type}!")


def tire_degradation(driver: Driver, gap):
    if gap > 5:
        dirt_air_influence = 1
    elif 3 <= gap <= 5:
        dirt_air_influence = 1.075
    elif 1.5 < gap < 3:
        dirt_air_influence = 1.3
    else: dirt_air_influence = 2

    if driver.tire_type == "Soft":
        if driver.tire_lap <= 5:
            driver.tire_wear -= 4 * dirt_air_influence
        elif driver.tire_lap <= 12:
            driver.tire_wear -= 5 * dirt_air_influence
        else:
            driver.tire_wear -= 7 * dirt_air_influence
    elif driver.tire_type == "Medium":
        if driver.tire_lap <= 10:
            driver.tire_wear -= 2 * dirt_air_influence
        elif driver.tire_lap <= 20:
            driver.tire_wear -= 3 * dirt_air_influence
        else:
            driver.tire_wear -= 5 * dirt_air_influence
    elif driver.tire_type == "Hard":
        if driver.tire_lap <= 10:
            driver.tire_wear -= 1 * dirt_air_influence
        elif driver.tire_lap <= 30:
            driver.tire_wear -= 2 * dirt_air_influence
        else:
            driver.tire_wear -= 4 * dirt_air_influence


    driver.tire_wear = max(0.0, driver.tire_wear)


def calculate_laptime(driver: Driver):
    base_laptime = 70
    base_power = 850

    power_influence = (base_power - driver.power) * 0.015

    lost_grip = 100.0 - driver.tire_wear

    if driver.tire_type == 'Soft':
        tire_influence = lost_grip * 0.015
    elif driver.tire_type == 'Medium':
        tire_influence = lost_grip * 0.012
    else:
        tire_influence = lost_grip * 0.008

    speed_influence = -(base_laptime * (driver.speed / 10000))
    experience_influence = -(base_laptime * (driver.experience / 10000))

    fuel_influence = driver.fuel_weight / 10 * 0.03
    driver.fuel_weight -= driver.fuel_management

    lap_time = base_laptime + power_influence + tire_influence + speed_influence + experience_influence + fuel_influence
    return lap_time


if __name__ == '__main__':

    drivers = []

    grid = int(input('Укажите количество гонщиков на старте гонки: '))

    total_laps = int(input('Укажите из скольки кругов будет состоять гонка: '))

    for i in range(grid):
        print(f"\n--- Создание гонщика #{i + 1} ---")
        name = input("Имя пилота: ")
        power = int(input("Мощность мотора (например, 850): "))
        tire_type = input("Стартовые шины (Soft/Medium/Hard): ")
        speed = int(input("Рейтинг скорости (0-100): "))
        experience = int(input("Рейтинг опыта (0-100): "))
        fuel_management = float(input("Расход топлива за круг (например, 3.2): "))
        pit_stop_quality = float(input("Качество пит-стопов команды (0-100): "))
        fuel_weight = 3.5 * randint(total_laps - 5, total_laps + 5)

        single_driver = Driver(name,power,tire_type,speed,experience,fuel_management,pit_stop_quality, fuel_weight)
        drivers.append(single_driver)

    for lap in range(1, total_laps + 1):
        standings = sorted(drivers, key=lambda x: x.total_time)

        for d in drivers:
            if not d.is_active:
                continue

            drs_active = False
            gap = 10.0

            if lap > 1:
                current_pos = standings.index(d)
                if current_pos > 0:
                    previous_driver = standings[current_pos - 1]
                    if previous_driver.is_active:
                        gap = d.total_time - previous_driver.total_time
                        if 0 < gap <= 1.0:
                            drs_active = True

            lap_t = calculate_laptime(d)
            if drs_active:
                lap_t -= 0.6

            d.total_time += lap_t
            d.tire_lap += 1
            tire_degradation(d, gap)

            if d.tire_wear < 30 and (total_laps - lap) > 6:
                if d.tire_type == 'Soft':
                    if (total_laps - lap) > 20: new_tire = 'Hard'
                    else: new_tire = 'Medium'
                    d.make_pitstop(lap, new_tire)
                elif d.tire_type == 'Medium':
                    if (total_laps - lap) > 20: new_tire = 'Hard'
                    else: new_tire = 'Soft'
                    d.make_pitstop(lap, new_tire)
                elif d.tire_type == 'Hard':
                    if (total_laps - lap) > 15: new_tire = 'Medium'
                    else: new_tire = 'Soft'
                    d.make_pitstop(lap, new_tire)

            if d.fuel_weight < d.fuel_management:
                print(f"[{lap}] === {d.name} СХОД: Закончилось топливо! ===")
                d.is_active = False

    finished_drivers = [d for d in drivers if d.is_active]
    finished_drivers.sort(key=lambda x: x.total_time)

    print("\n--- ИТОГОВЫЕ РЕЗУЛЬТАТЫ ---")
    for place, d in enumerate(finished_drivers, 1):
        minutes = int(d.total_time // 60)
        seconds = d.total_time % 60
        print(f"{place}. {d.name} | Итоговое время: {minutes}м {seconds:.3f}с")

    dof_drivers = [d for d in drivers if not d.is_active]
    if dof_drivers:
        print("\n--- НЕ ФИНИШИРОВАЛИ (DNF) ---")
        for d in dof_drivers:
            print(f"• {d.name}")