import unstructured_client
from unstructured_client.models import shared
import json
from datetime import datetime

# Replace with your actual API key
API_KEY = "P1r3t1LKCyHhVQNjfyJm0a4yzhcpxd"

# Initialize the client
client = unstructured_client.UnstructuredClient(
    api_key_auth=API_KEY,
    server_url="https://api.unstructuredapp.io",
)

# Replace with the path to your file
filename = "/Users/mainframe/Developer/ai_engineer/rag-weave/data/test_files/FAQ Data collection.pdf"

# Read the file
with open(filename, "rb") as f:
    file_content = f.read()

# Prepare the request
request = shared.PartitionParameters(
    files=shared.Files(
        content=file_content,
        file_name=filename,
    ),
    strategy=shared.Strategy.AUTO,
    languages=["eng"],
)

# Call the API
try:
    response = client.general.partition(request=request)

    # Print the first element of the response
    if response.elements:
        print("First element of the response:")
        print(response.elements[0])
    else:
        print("No elements in the response.")

    # Print the total number of elements
    print(f"\nTotal number of elements: {len(response.elements)}")

    # Save the response to disk
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"unstructured_response_{timestamp}.json"

    # The elements are already dictionaries, so we can save them directly
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(response.elements, f, ensure_ascii=False, indent=4)

    print(f"\nResponse saved to {output_filename}")

except Exception as e:
    print(f"An error occurred: {e}")
