from confluence_integration.confluence_client import ConfluenceClient
from space.manager import Space


def main():
    print("Retrieving all spaces from Confluence...")
    client = ConfluenceClient()
    spaces = client.retrieve_space_list()
    print(f"Retrieved {len(spaces)} spaces from Confluence.")
    global_spaces = [s for s in spaces if s.get('type') == 'global']
    print(f"Found {len(global_spaces)} global spaces.")
    for idx, space in enumerate(global_spaces, 1):
        key = space.get('key')
        name = space.get('name')
        print(f"\n[{idx}/{len(global_spaces)}] Processing global space: {name} (Key: {key})")
        Space().load_new(key, name)
    print("\nAll global spaces processed.")

if __name__ == "__main__":
    main() 