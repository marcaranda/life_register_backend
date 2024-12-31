from googletrans import Translator
import requests

translator = Translator()
apiURl = 'https://api.edamam.com/api/nutrition-details?app_id=e9fe60f1&app_key=85a5d60746f78895d03ec97e5f4e59a7'

async def get_meal_macros(meal):
  apiText = {
    "title": "Meal",
    "ingr": []
  }

  for item in meal:
    englishName = translator.translate(item.name, src='es', dest='en').text
    ingredient = f"{item.quantity} {'grams' if item.unit == 'g' else 'unit'} {englishName}"
    apiText["ingr"].append(ingredient)
  
  response = requests.post(apiURl, json=apiText)
  data = response.json()

  macros = {
    "Calorías": f"{data['totalNutrients']['ENERC_KCAL']['quantity']} {data['totalNutrients']['ENERC_KCAL']['unit']}",
    "Grasas": {
      "Grasas totales": f"{data['totalNutrients']['FAT']['quantity']} {data['totalNutrients']['FAT']['unit']}",
      "Grasas saturadas": f"{data['totalNutrients']['FASAT']['quantity']} {data['totalNutrients']['FASAT']['unit']}",
    },
    "Carbohidratos": {
      "Carbohidratos totales": f"{data['totalNutrients']['CHOCDF']['quantity']} {data['totalNutrients']['CHOCDF']['unit']}",
      "Azúcares": f"{data['totalNutrients']['SUGAR']['quantity']} {data['totalNutrients']['SUGAR']['unit']}",
    },
    "Proteínas": f"{data['totalNutrients']['PROCNT']['quantity']} {data['totalNutrients']['PROCNT']['unit']}",
  }

  return macros