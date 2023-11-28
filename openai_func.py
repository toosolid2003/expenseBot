from openai import OpenAI
import json

funcs = [
            # {
            #     "type":"function",
            #     "function": {
            #         "name":"get_category",
            #         "description": "Cateogize the business expense with a tax-fridnely category",
            #         "parameters":   {
            #                 "type":"object",
            #                 "properties":   {
            #                     "exp_category":  {
            #                         "type": "string",
            #                         "description":"infer the category of the business expense being submitted"
            #                 },
            #             }
            #             },
            #         },
            #     },
                {
                    "type":"function",
                    "function": {
                        "name":"get_expense_data",
                        "description":"Extract the amount, currency, description and cateogry of the business expense",
                        "parameters":   {
                            "type":"object",
                            "properties":   {
                                "amount":   {
                                    "type":"integer",
                                    "description":"amount of the expense in numerical form"
                                },
                                "currency": {
                                    "type":"string",
                                    "description":"currency of the expense in ISO format or 3 capital letters"
                                },
                                "description":  {
                                    "type":"string",
                                    "description":"Reason for the expense"
                                },
                                "category": {
                                    "type":"string",
                                    "description": "from the description of the expense, infer a tax-friendly category of the expense"
                                },
                            },
                        },
                    },
                },
]

sample_input = [
    '129 euros for hotel night Paris',
    'train ticket for Bali $45',
    '500 liras, coffee in Istanbul',
    'fuel Almeria 55.5 euros',
    'record an expense of 550 euros for hotel in Berlin'
]

for sample in sample_input:
    client = OpenAI(api_key="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")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages = [{"role":"user","content":sample}],
        tools=funcs,
        tool_choice="auto"
    )

    r = response.choices[0].message.tool_calls[0].function.arguments
    json_r = json.loads(r) 
    print(r)
