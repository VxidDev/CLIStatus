import argparse , subprocess , requests , datetime , psutil , os
from colorama import Style , Fore , init

init()

time = datetime.datetime.now()

def main():
    parser = argparse.ArgumentParser(description="Lightweight utility, that helps monitoring system status and way more!")
    
    parser.add_argument("-w" , "--weather" , type=str, help="Check weather!")
    parser.add_argument("-r" , "--ram" , action="store_true" , help="Get RAM usage!")
    parser.add_argument("-c" , "--cpu" , action="store_true" , help="Get CPU usage!")
    parser.add_argument("-d" , "--disk" , action="store_true" , help="Get disk usage!")

    args = parser.parse_args()

    if args.weather:
        print(f"Fetching" + Style.BRIGHT + Fore.WHITE , "Geocode..." + Style.RESET_ALL)
        headers = {"User-Agent": "CLIStatus/1.0"}
        geocoding_req = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={args.weather}&count=1&language=en" , headers=headers)
        if geocoding_req.status_code == 200:
            try:
                geocoding_json = geocoding_req.json()
                geocode = [geocoding_json["results"][0]["latitude"] , geocoding_json["results"][0]["longitude"]]
                country = geocoding_json["results"][0]["country"]         
            except KeyError:
                print(Style.BRIGHT + Fore.RED + "request failed" + Style.RESET_ALL + ": unknown city!")           
                return 0
        else:
            print(Style.BRIGHT + Fore.RED + "request failed" + Style.RESET_ALL + f": {geocoding_req.status_code}")
            return 0
        print("Fetching" + Style.BRIGHT + Fore.WHITE , "Temperature..." + Style.RESET_ALL)
        weather_req = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={geocode[0]}&longitude={geocode[1]}&hourly=temperature_2m,rain&forecast_days=1")
        if weather_req.status_code == 200:
            weather_json = weather_req.json()
            print(country , "," , args.weather , time.strftime("%D"))
            for i in range(int(time.strftime("%H")) , 24):
                if weather_json["hourly"]["temperature_2m"][i] <= 10:
                    color = Fore.CYAN
                elif 10 < weather_json["hourly"]["temperature_2m"][i] <= 20:
                    color = Fore.GREEN
                elif 20 < weather_json["hourly"]["temperature_2m"][i] < 30:
                    color = Fore.YELLOW
                else:
                    color = Fore.RED

                if weather_json["hourly"]["rain"][i] > 0:
                    weather = f"rain: {weather_json["hourly"]["rain"][i]} mm"
                else:
                    weather = ""

                print(f"{i}:00 :" + Style.BRIGHT + color , f"{weather_json["hourly"]["temperature_2m"][i]} °C" + Style.RESET_ALL + Style.BRIGHT + Fore.BLUE , weather , Style.RESET_ALL)
        else:
            print(Style.BRIGHT + Fore.RED + "request failed" + Style.RESET_ALL + ": {weather_req.status_code}")
    
    if args.ram:
        ram_usage = psutil.virtual_memory()
        ram_used = round(((ram_usage.total - ram_usage.available) / 1024 ** 3) , 2)
        total_ram_usage = round((ram_usage.total / 1024 ** 3) , 2) 
        if ram_used <= total_ram_usage / 100 * 30:
            color = Fore.GREEN
        elif total_ram_usage / 100 * 30 < ram_used <= total_ram_usage / 100 * 75:
            color = Fore.YELLOW
        else:
            color = Fore.RED
        print(Style.BRIGHT + color +f"{ram_used}" + " GiB /" , total_ram_usage , "GiB" + Style.RESET_ALL)
    if args.cpu:
        print("Testing " + Style.BRIGHT + Fore.WHITE + "CPU usage..." + Style.RESET_ALL)
        core_usage = psutil.cpu_percent(interval=5 , percpu=True)
        if os.name == "posix":
            cpu_name = subprocess.run("lscpu | grep 'Model name'" , shell=True , capture_output=True , text=True).stdout.removeprefix("Model name:").strip()
        else:
            cpu_name = "CPU"
        amount_of_cores = len(core_usage)
        sum_of_core_usage = sum(core_usage)
        average_usage = round(sum_of_core_usage / amount_of_cores , 2)
        if average_usage <= 30:
            color = Fore.GREEN
        elif 30 < average_usage <= 75:
            color = Fore.YELLOW 
        else:
            color = Fore.RED 
        print(cpu_name + ":" , Style.BRIGHT + color + f"{average_usage}% / 100%")

    if args.disk:
        disk_usage = psutil.disk_usage("/")
        if disk_usage.used <= disk_usage.total / 100 * 30:
            color = Fore.GREEN 
        elif 30 < disk_usage.used < disk_usage.total / 100 * 75:
            color = Fore.YELLOW 
        else:
            color = Fore.RED 
        print(Style.BRIGHT + color + f"{round((disk_usage.used / 1024 ** 3) , 2)}" + " GiB / " + f"{round((disk_usage.total / 1024 ** 3) , 2)}" + " GiB" + Style.RESET_ALL)

if __name__ == "__main__":
    main()
