from core.pipeline import answer_query

while True:
    query = input("Enter query: ")

    result = answer_query(query)

    print("\nSource:", result["source"])
    print("Answer:\n", result["answer"])
    print("-" * 50)
