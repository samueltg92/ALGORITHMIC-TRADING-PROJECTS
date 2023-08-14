from forex_python.converter import CurrencyRates
import time

def display_exchange_rates(base_currency, target_currencies):
    c = CurrencyRates()
    print("-------------------------")
    for currency in target_currencies:
        rate = c.get_rate(base_currency, currency)
        print(f"{base_currency}/{currency}: {rate}")

if __name__ == "__main__":
    base_currency = "EUR"
    target_currencies = ["USD", "JPY", "GBP", "AUD"]  # Add more currencies as needed
    while True:
        display_exchange_rates(base_currency, target_currencies)
        time.sleep(1)  # Display rates every second
