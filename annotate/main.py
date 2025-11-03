import json

def get_entity_positions(sentence: str, entity: str):
    """
    Returns the start and end index of the given entity in the sentence.
    If not found, returns -1 for both.
    """
    entity_start = sentence.lower().find(entity.lower())
    entity_end = entity_start + len(entity) if entity_start != -1 else -1
    return entity_start, entity_end


def process_entity_data(data):
    """
    Processes a list of dicts containing 'sentence' and 'entity' keys.
    Returns a new list with entity_start and entity_end included.
    """
    results = []
    for item in data:
        sentence = item.get("sentence", "")
        entity = item.get("entity", "")
        start, end = get_entity_positions(sentence, entity)
        results.append({
            "sentence": sentence,
            "entity": entity,
            "entity_start": start,
            "entity_end": end
        })
    return results

if __name__ == "__main__":
    # Example input data
    input_data = [
    {
        "entity": "anterior abdominal hernia",
        "sentence": "AM\nDescription\nPlanned Procedure:\n(49593): Catalog Name: Repair of anterior abdominal hernia (epigastric,\nincisional, ventral, umbilical, spigelian), any approach ("
      },
     {
            "entity": "abdominal hernia",
            "sentence": "AM\nDescription\nPlanned Procedure:\n(49593): Catalog Name: Repair of anterior abdominal hernia (epigastric,\nincisional, ventral, umbilical, spigelian), any approach ("
    }
    ]
    output_data = process_entity_data(input_data)
    print(json.dumps(output_data, indent=2))