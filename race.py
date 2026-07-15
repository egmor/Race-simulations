import json
import os
import time
from random import *

tire = ['soft', 's', 'софт', 'мягкие', 'medium', 'm', 'мудиум', 'средние', 'hard', 'h', 'хард', 'жёсткие']


class Driver:
    def __init__(self, name, team, power, tire_type, speed, experience, fuel_management, pit_stop_quality, fuel_weight):
        self.name = name
        self.team = team
        self.power = power
        self.tire_type = tire_type
        self.speed = speed
        self.experience = experience
        self.fuel_management = fuel_management
        self.pit_stop_quality = pit_stop_quality

        self.tire_lap = 0
        self.total_time = 0.0
        self.lap_time = 0
        self.tire_wear = 100.0

        self.fuel_weight = fuel_weight
        self.is_active = True

    def make_pitstop(self, lap, new_tire_type, gap, choice):
        self.tire_type = new_tire_type
        self.tire_lap = 0
        self.tire_wear = 100.0
        chance_mistake = 100 - self.pit_stop_quality
        mistake = randint(1, 100)
        base_change_time = 3.0 - round(uniform(0, (self.pit_stop_quality / 100.0)), 3)

        return_loss = 10.0 if (VSC or SC) else 20.0

        if mistake <= chance_mistake:
            mistake_time = round(uniform(1.0, 3.5), 3)
            tire_change_time = base_change_time + mistake_time
            if choice == "First":
                print(f"[{lap}]  {self.name} заехал на пит-стоп под обменом флагов. ЗАМИНКА: +{mistake_time}с (Всего: {tire_change_time:.3f}с) -> {self.tire_type}")
        else:
            tire_change_time = base_change_time
            if choice == "First":
                print(f"[{lap}] {self.name} заехал на пит-стоп. Чистая работа за {tire_change_time:.3f}с -> {self.tire_type}")

        self.total_time += return_loss + tire_change_time
        gap += return_loss + tire_change_time
        return gap, tire_change_time


def tire_degradation(driver: Driver, gap):
    if gap > 5:
        dirt_air_influence = 1
    elif 3 <= gap <= 5:
        dirt_air_influence = 1.075
    elif 1.5 < gap < 3:
        dirt_air_influence = 1.3
    else:
        dirt_air_influence = 2

    if SC or VSC:
        dirt_air_influence *= 0.33

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

    random_range = 0.35 - (driver.experience / 100.0) * 0.30
    lap_time = uniform(lap_time - random_range, lap_time + random_range)
    
    return lap_time


def retire(driver: Driver, lap, total_lap, choice):
    retire_chance = max(1, int((lap / total_lap) * 10))

    if randint(1, 1000) == retire_chance:
        driver.is_active = False
        if choice == "First":
            cause_retire = randint(1, 5)
            if cause_retire == 1:
                print(f"[{lap}]  У пилота {driver.name} случился прокол, и он сошёл.")
            elif cause_retire == 2:
                print(f"[{lap}] ⚙ У пилота {driver.name} сломалась гидравлика, и он сошёл.")
            elif cause_retire == 3:
                print(f"[{lap}]  У пилота {driver.name} сломалась силовая установка, и он сошёл.")
            elif cause_retire == 4:
                print(f"[{lap}]  Пилот {driver.name} ошибся на входе в поворот и сошёл.")
            else:
                print(f"[{lap}]  У пилота {driver.name} сломалась коробка передач, и он сошёл.")
        return True
    return False


def check_safety_car(out_drivers, lap, current_vsc, current_sc, current_rf):
    if out_drivers:
        if not (current_vsc or current_sc or current_rf):
            if len(out_drivers) == 1:
                print(f"\n[{lap}]  ВНИМАНИЕ: На трассе обломки машины {out_drivers[0]}. Включен режим Virtual Safety Car (VSC)!")
                return True, False, False, lap
            elif len(out_drivers) == 2:
                print(f"\n[{lap}]  БЕЗОПАСНОСТЬ: Серьезная авария! {out_drivers[0]} и {out_drivers[1]} столкнулись. На трассу выходит Safety Car (SC)!")
                return False, True, False, lap
            elif len(out_drivers) >= 3:
                print(f"\n[{lap}]  КРАСНЫЙ ФЛАГ: Массовый завал! Гонка остановлена красными флагами!")
                return False, False, True, lap

    return current_vsc, current_sc, current_rf, 0


if __name__ == '__main__':
    drivers = []
    best_lap = [100.0, '', 0]
    best_pit_stop = [100.0, '', '', 0]

    total_laps = int(input('Укажите из скольки кругов будет состоять гонка: '))
    file_name = "drivers.json"

    print("--- НАСТРОЙКА ПЕЛЕТОНА ---")

    if os.path.exists(file_name):
        use_file = input(f"Найден файл '{file_name}'. Загрузить гонщиков из него? (y/n): ").strip().lower()

        if use_file == 'y':
            try:
                with open(file_name, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                for item in data:
                    fuel_weight = 4.5 * randint(total_laps - 5, total_laps + 5)

                    single_driver = Driver(
                        name=item["name"],
                        team=item["team"],
                        power=int(item["power"]),
                        tire_type=item["tire_type"],
                        speed=int(item["speed"]),
                        experience=int(item["experience"]),
                        fuel_management=float(item["fuel_management"]),
                        pit_stop_quality=float(item["pit_stop_quality"]),
                        fuel_weight=fuel_weight
                    )
                    drivers.append(single_driver)

                print(f"Успешно загружено гонщиков: {len(drivers)}")

            except Exception as e:
                print(f"Ошибка при чтении файла: {e}. Переходим к ручному вводу.")
                drivers = []

    if not drivers:
        print("\n[] Запуск ручного создания гонщиков...")
        grid = int(input('Укажите количество гонщиков на старте гонки: '))

        for i in range(grid):
            print(f"\n--- Создание гонщика #{i + 1} ---")
            name = input("Имя пилота: ")
            team = input("Название команды: ")
            power = int(input("Мощность мотора (например, 850): "))
            tire_type = input("Стартовые шины (Soft/Medium/Hard): ")
            speed = int(input("Рейтинг скорости (0-100): "))
            experience = int(input("Рейтинг опыта (0-100): "))
            fuel_management = float(input("Расход топлива за круг (например, 3.2): "))
            pit_stop_quality = float(input("Качество пит-стопов команды (0-100): "))
            fuel_weight = 4.5 * randint(total_laps - 1, total_laps + 5)

            single_driver = Driver(name, team, power, tire_type, speed, experience, fuel_management, pit_stop_quality,
                                   fuel_weight)
            drivers.append(single_driver)

    choice = input("Вы хотите видеть подробную гонку по кругам или сразу результат? (First/Second) ").strip()

    VSC = SC = RF = False
    safety_lap = 0
    sc_duration = 3
    pit_stop = 1000

    for lap in range(1, total_laps + 1):
        if (VSC or SC) and (lap - safety_lap >= sc_duration):
            if choice == "First":
                if VSC: print(f"[{lap}]  Режим VSC завершен. Рестарт!")
                if SC: print(f"[{lap}]  Safety Car покидает трассу на этом круге. ЗЕЛЕНЫЙ ФЛАГ!")
            VSC = SC = False
            safety_lap = 0

        out_drivers = []
        standings = sorted(drivers, key=lambda x: x.total_time)
        start_lap_times = {drv.name: drv.total_time for drv in drivers}

        for d in standings:
            if not d.is_active:
                continue

            d.lap_time = calculate_laptime(d)

            if retire(d, lap, total_laps, choice):
                out_drivers.append(d.name)
                continue

            drs_active = False
            overtaking = False
            gap = 10.0

            if lap > 1 and not VSC and not SC:
                current_pos = standings.index(d)
                if current_pos > 0:
                    previous_driver = standings[current_pos - 1]
                    if previous_driver.is_active:
                        gap = start_lap_times[d.name] - start_lap_times[previous_driver.name]

                        if 0 < gap <= 1.0:
                            drs_active = True
                            speed_advantage = previous_driver.lap_time - d.lap_time

                            if randint(1, 200) == 12:
                                previous_driver.is_active = False
                                d.is_active = False
                                out_drivers.append(previous_driver.name)
                                out_drivers.append(d.name)
                                if choice == "First": print(f"[{lap}]  Столкновение! {d.name} жестко атаковал {previous_driver.name} в зоне DRS. Двойной сход.")
                                continue

                            elif randint(1, 20) == 7:
                                previous_driver.total_time += 1.5
                                d.lap_time += 4.5
                                if choice == "First": print(f"[{lap}]  Контакт! {d.name} зацепил машину {previous_driver.name} при попытке обгона. Оба теряют время.")

                            elif (speed_advantage > 0 and randint(1, 4) == 2) or (randint(1, 5) <= 3):
                                overtaking = True
                                if choice == "First": print(f"[{lap}]  {d.name} проходит {previous_driver.name} в конце прямой")

                            elif randint(1, 100) <= 8:
                                mistake_time = round(uniform(0.5, 1.5), 3)
                                previous_driver.lap_time += mistake_time
                                if choice == "First": print(f"[{lap}]  {previous_driver.name} ошибся под давлением {d.name} и потерял +{mistake_time}с")

                            else:
                                d.lap_time = previous_driver.lap_time + round(uniform(0.1, 0.35), 3)
                                if choice == "First": print(f"[{lap}]  {d.name} застрял за {previous_driver.name} и теряет темп.")

            if drs_active:
                d.lap_time -= 0.6
            if overtaking:
                d.lap_time -= 0.1

            if VSC:
                d.lap_time *= 1.4
                d.total_time += d.lap_time
            elif SC:
                d.lap_time = 110.0
                d.total_time += d.lap_time
            else: d.total_time += d.lap_time


            if not VSC and not SC:
                if best_lap[0] > d.lap_time:
                    best_lap[0] = d.lap_time
                    best_lap[1] = d.name
                    best_lap[2] = lap

            d.tire_lap += 1
            tire_degradation(d, gap)

            if d.fuel_weight < d.fuel_management:
                if choice == "First":
                    print(f"[{lap}] === {d.name} СХОД: Закончилось топливо ===")
                d.is_active = False
                out_drivers.append(d.name)

            if d.tire_wear < 30 and (total_laps - lap) > 6:
                if d.tire_type == 'Soft':
                    new_tire = 'Hard' if (total_laps - lap) > 20 else 'Medium'
                    gap, pit_stop = d.make_pitstop(lap, new_tire, gap, choice)
                elif d.tire_type == 'Medium':
                    new_tire = 'Hard' if (total_laps - lap) > 20 else 'Soft'
                    gap, pit_stop = d.make_pitstop(lap, new_tire, gap, choice)
                elif d.tire_type == 'Hard':
                    new_tire = 'Medium' if (total_laps - lap) > 15 else 'Soft'
                    gap, pit_stop = d.make_pitstop(lap, new_tire, gap, choice)

                if best_pit_stop[0] > pit_stop:
                    best_pit_stop[0] = pit_stop
                    best_pit_stop[1] = d.name
                    best_pit_stop[2] = d.team
                    best_pit_stop[3] = lap

        if SC:
            sc_standings = sorted([drv for drv in drivers if drv.is_active], key=lambda x: x.total_time)
            for place, drv in enumerate(sc_standings):
                if place > 0:
                    drv.total_time = sc_standings[place - 1].total_time + round(uniform(0.5, 1.2), 3)

        active_standings = sorted([drv for drv in drivers if drv.is_active], key=lambda x: x.total_time)

        if choice == "First":
            time.sleep(2)
            print(f"\n================ КОНЕЦ {lap} КРУГА ================")
            if VSC:
                print(" РЕЖИМ VSC (Ограничение скорости на 40%) ")
            elif SC:
                print(" РЕЖИМ SAFETY CAR (Пелотон собран вместе) ")
            print("Текущий Топ-10:")
            for place, drv in enumerate(active_standings[:10], 1):
                if place == 1:
                    print(f" {place}.  {drv.name:20} ({drv.team}) | Interval")
                else:
                    gap = drv.total_time - active_standings[place - 2].total_time
                    time.sleep(gap * 0.15 if not SC else 0.05)
                    print(f" {place}. {drv.name:20} ({drv.team}) | +{gap:.3f}с")
            print("==================================================\n")

        new_vsc, new_sc, new_rf, trigger_lap = check_safety_car(out_drivers, lap, VSC, SC, RF)
        if trigger_lap > 0:
            VSC, SC, RF = new_vsc, new_sc, new_rf
            safety_lap = trigger_lap

        if RF:
            print("\n ГОНКА ОСТАНОВЛЕНА КРАСНЫМ ФЛАГОМ! Результаты заморожены.")
            break

    # Финал гонки
    finished_drivers = [d for d in drivers if d.is_active]
    finished_drivers.sort(key=lambda x: x.total_time)

    if not finished_drivers:
        print("\nНи один пилот не смог финишировать в этой безумной гонке!")
    else:
        leader_time = finished_drivers[0].total_time

        print("\n--- ИТОГОВЫЕ РЕЗУЛЬТАТЫ ---")
        for place, d in enumerate(finished_drivers, 1):
            minutes = int(d.total_time // 60)
            seconds = d.total_time % 60
            if d.total_time == leader_time:
                if seconds < 10: print(f"{place}. {d.name:20} | Итоговое время: {minutes}.0{seconds:.3f}")
                else: print(f"{place}. {d.name:20} | Итоговое время: {minutes}.{seconds:.3f}")
            else:
                gap_minutes = int((d.total_time - leader_time) // 60)
                gap_seconds = (d.total_time - leader_time) % 60
                if seconds < 10 and gap_minutes == 0: print(f"{place}. {d.name:20} | Отставание: +{gap_seconds:.3f}| Итоговое время: {minutes}:0{seconds:.3f}")
                elif seconds > 10 and gap_minutes == 0: print(f"{place}. {d.name:20} | Отставание: +{gap_seconds:.3f}| Итоговое время: {minutes}:{seconds:.3f}")
                elif seconds < 10 and gap_seconds < 10: print(f"{place}. {d.name:20} | Отставание: +{gap_minutes}:0{gap_seconds:.3f}| Итоговое время: {minutes}:0{seconds:.3f}")
                elif seconds > 10 and gap_seconds < 10: print(f"{place}. {d.name:20} | Отставание: +{gap_minutes}:0{gap_seconds:.3f}| Итоговое время: {minutes}:{seconds:.3f}")
                elif seconds < 10 and gap_seconds > 10: print(f"{place}. {d.name:20} | Отставание: +{gap_minutes}:{gap_seconds:.3f}| Итоговое время: {minutes}:0{seconds:.3f}")
                else: print(f"{place}. {d.name:20} | Отставание: +{gap_minutes}:{gap_seconds:.3f}| Итоговое время: {minutes}:{seconds:.3f}")

    dof_drivers = [d for d in drivers if not d.is_active]
    if dof_drivers:
        print("\n--- НЕ ФИНИШИРОВАЛИ (DNF) ---")
        for d in dof_drivers: print(f"• {d.name}")

    if best_lap[1]:
        print("\n--- ЛУЧШИЙ КРУГ ---")
        minutes = int(best_lap[0] // 60)
        seconds = best_lap[0] % 60
        if seconds < 10: print(f"{best_lap[1]} | {best_lap[2]} круг |  {minutes}:0{seconds:.3f}")
        else: print(f"{best_lap[1]} | {best_lap[2]} круг |  {minutes}:{seconds:.3f}")

    if best_pit_stop[1]:
        print("\n--- ЛУЧШИЙ ПИТ-СТОП ---")
        print(f"{best_pit_stop[2]} | {best_pit_stop[3]} круг | {best_pit_stop[1]} | {best_pit_stop[0]:.3f} ")