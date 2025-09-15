import argparse , requests , datetime 
from colorama import Style , Fore , init

init()

time = datetime.datetime.now()

def main():
    parser = argparse.ArgumentParser(description="Lightweight utility, that helps monitoring system status and way more!")
    
    parser.add_argument("-w" , "--weather" , type=str, help="Check weather!")

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

if __name__ == "__main__":
    main()
