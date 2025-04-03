import os
import re
from owlready2 import  get_ontology, Thing, DataProperty, ObjectProperty
import uuid 

# Define the file path for the ontology
# Using an absolute path ensures it works regardless of where Jupyter is launched from.
# Change 'YourUsername', 'path', 'to', 'your', 'project' appropriately
# Or, if the notebook is in the same folder you want the .owl file, you can simplify:
# ontology_file = "news_ontology_interactive.owl"
project_directory = os.getcwd() # Get current working directory where notebook is running
ontology_file = os.path.join(project_directory, "data", "news_ontology_interactive.owl")

print(f"Ontology file path: {ontology_file}")

# Create or load the ontology
# The 'file://' prefix is important for Owlready2 to treat it as a local file URI
try:
    # Try loading if it exists
    onto = get_ontology(f"file://{os.path.abspath(ontology_file)}").load()
    print("Ontology loaded successfully.")
except FileNotFoundError:
    print("Ontology file not found. A new one will be created on save.")
    base_iri = "http://test.org/news_ontology.owl#"
    onto = get_ontology(base_iri)
except Exception as e:
    print(f"Error loading ontology: {e}. Proceeding with empty/new ontology.")


print(f"Ontology IRI: {onto.base_iri}")


with onto:
    # Base Classes
    class News(Thing): 
        pass
    class Entity(Thing): 
        pass
    class Category(Thing): 
        pass # Topics like Sports, Politics

    # Subclasses of Entity
    class Person(Entity): 
        pass
    class Organization(Entity): 
        pass
    class Location(Entity): 
        pass
    class NewsSource(Organization): 
        pass # Specific type of Organization

    # Data Properties (Attributes)
    class hasTitle(DataProperty):
        domain = [News]
        range = [str]

    class hasSourceString(DataProperty): # The literal source name string
        domain = [News]
        range = [str]

    class hasFullText(DataProperty):
        domain = [News]
        range = [str]

    class hasTimestamp(DataProperty): # Store as string for simplicity now
        domain = [News]
        range = [str] # Could use datetime if needed

    class hasEntityName(DataProperty): # Name of Person, Org, Location, NewsSource
        functional = True # An entity has exactly one canonical name in this model
        domain = [Entity]
        range = [str]

    class hasCategoryName(DataProperty): # Name of the category (e.g., "Sports")
        functional = True
        domain = [Category]
        range = [str]

    # Object Properties (Relationships)
    class publishedBy(ObjectProperty):
        domain = [News]
        range = [NewsSource]

    class hasCategory(ObjectProperty):
        domain = [News]
        range = [Category]

    class mentionsEntity(ObjectProperty):
        domain = [News]
        range = [Entity]

print("--- Ontology Classes and Properties Defined (within 'onto' object) ---")

# Map entity type strings (from simulated NER) to ontology classes
entity_class_map = {
    "Person": onto.Person,
    "Organization": onto.Organization,
    "Location": onto.Location,
    # Add more mappings if your NER simulation produces other types
}

def sanitize_iri(name):
    """Creates a safer IRI fragment from a name."""
    if not name: 
        return "unnamed_entity"
    # Remove characters not suitable for IRIs and replace spaces
    name = re.sub(r'[^\w\s-]', '', name).strip()
    name = re.sub(r'\s+', '_', name)
    return name if name else "unnamed_entity"

def find_or_create(onto_instance, cls, name_prop, name_value):
    """
    Searches for an individual of class 'cls' with 'name_prop' == 'name_value'.
    If not found, creates a new individual. Ensures uniqueness based on name.
    Returns the found or created individual.
    """
    if not name_value: # Cannot create/find without a name
        print(f"Warning: Attempted to find/create {cls.__name__} with empty name.")
        return None

    # Search using the functional name property. Access property via its name attribute.
    query = {name_prop.name: name_value}
    # Ensure search is within the correct ontology namespace if needed, though search_one often handles this.
    found_individual = onto_instance.search_one(type=cls, **query)

    if found_individual:
        #print(f"Found existing {cls.__name__}: {name_value}")
        return found_individual
    else:
        # Create a new one
        safe_name = sanitize_iri(name_value)
        # Generate a unique IRI using UUID to prevent clashes even with same sanitized names
        individual_iri = f"{onto_instance.base_iri}{safe_name}_{cls.__name__}_{uuid.uuid4().hex[:8]}"

        # Create the individual in the specific ontology namespace
        new_individual = cls(individual_iri, namespace=onto_instance)

        # Set the name property using attribute access
        getattr(new_individual, name_prop.name).append(name_value)
        #print(f"Created new {cls.__name__}: {name_value} (IRI: {new_individual.iri})")
        return new_individual
    
news_counter = 0 # Simple way to generate unique article IRIs

def add_news_to_ontology(onto_instance, news_data, simulated_entities):
    """Processes news data and simulated NER output to populate the ontology."""
    global news_counter
    print(f"\n--- Processing News: {news_data['text']} ---")

    # 2.1 Get or Create Source Individual
    source_name = "TestSource" # For now
    source_individual = find_or_create(onto_instance, onto.NewsSource, onto.hasEntityName, source_name)
    if not source_individual:
        print(f"  Skipping article - Could not find/create source: {source_name}")
        return None

    # 2.2 Get or Create Category Individual
    category_name = "TestCategory" # For now
    category_individual = find_or_create(onto_instance, onto.Category, onto.hasCategoryName, category_name)
    if not category_individual:
         # Allowing articles without category for flexibility, could skip if required
        print(f"  Warning: Could not find/create category: {category_name}. Proceeding without category link.")
        # continue

    # 2.3 Create NewsArticle Individual
    news_counter += 1
    article_iri_name = f"article_{str(news_counter)}"
    article = onto.News(article_iri_name, namespace=onto_instance)

    # Assign data properties
    article.hasTitle.append("TestTitle")
    article.hasTimestamp.append("Now")
    article.hasFullText.append(news_data['text'])
    article.hasSourceString.append("TestSource")

    # Assign object properties (links)
    article.publishedBy.append(source_individual)
    if category_individual: # Only link if category was found/created
        article.hasCategory.append(category_individual)

    print(f"  Created News: {article.name}")
    print(f"    Linked to Source: {source_individual.hasEntityName.first()}")
    if category_individual:
         print(f"    Linked to Category: {category_individual.hasCategoryName.first()}")


    # --- Process and Link Mentioned Entities ---
    mentioned_entities_in_article = []
    #simulated_entities = ner_outputs_list[i]

    print(f"    Processing {len(simulated_entities)} simulated entities...")
    for entity_name, entity_type_str in simulated_entities:
        entity_class = entity_class_map.get(entity_type_str)
        if not entity_class:
            print(f"      Warning: Unknown entity type '{entity_type_str}' for '{entity_name}'. Skipping.")
            continue

        # Use find_or_create for entities
        entity_individual = find_or_create(onto_instance, entity_class, onto.hasEntityName, entity_name)
        if entity_individual:
            # Avoid adding duplicate links if NER list has duplicates
            if entity_individual not in mentioned_entities_in_article:
                mentioned_entities_in_article.append(entity_individual)
                print(f"      Found/Created & Linked Entity: {entity_individual.hasEntityName.first()} ({entity_class.__name__})")

    # Link article to all its unique mentioned entities
    article.mentionsEntity = mentioned_entities_in_article

    return article

# Load the ontology when this module is imported

def load_ontology():
    """Loads the ontology from the file."""
    global onto
    global entity_class_map
    
    onto = get_ontology(f"file://{os.path.abspath(ontology_file)}").load()
    entity_class_map = {
        "Person": onto.Person,
        "Organization": onto.Organization,
        "Location": onto.Location,
        # Add more mappings if your NER simulation produces other types
    }

load_ontology()

print("--- Ontology Manager Loaded ---")