from utils.live_fallback import nagaland_live_search

query = input("Enter query: ")

result = nagaland_live_search(query)

if result:
    print("\nLive Result:\n")
    print(result)
else:
    print("\nNo Nagaland-related live result found.")
