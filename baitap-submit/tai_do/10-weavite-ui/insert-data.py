import pandas as pd
import weaviate
from weaviate.classes.config import Configure, Property, DataType, Tokenization

# Define Weaviate and connect
vector_db_client = weaviate.connect_to_local(
    # # Update if any changes
    # host="127.0.0.1",
    # port=8080,
    # grpc_port=50051,
    # skip_init_checks=True
)

vector_db_client.connect()
print("DB is ready: {}".format(vector_db_client.is_ready()))

COLLECTION_NAME = "BookCollection"

def create_collection():
    # Create schema for collection
    movie_collection = vector_db_client.collections.create(
        name=COLLECTION_NAME,
        # Use model transformers to create vector
        vectorizer_config=Configure.Vectorizer.text2vec_transformers(),
        properties=[
            Property(name="title", data_type=DataType.TEXT,
                     vectorize_property_name=True, tokenization=Tokenization.LOWERCASE),
            Property(name="author", data_type=DataType.TEXT,
                     vectorize_property_name=True, tokenization=Tokenization.LOWERCASE),
            Property(name="description", data_type=DataType.TEXT,
                     vectorize_property_name=True, tokenization=Tokenization.LOWERCASE),
            Property(name="genre", data_type=DataType.TEXT,
                     vectorize_property_name=True, tokenization=Tokenization.LOWERCASE),
            Property(name="grade", data_type=DataType.TEXT,
                    skip_vectorization=True),
            Property(name="lexile", data_type=DataType.TEXT,
                    skip_vectorization=True),
            Property(name="path", data_type=DataType.TEXT,
                    skip_vectorization=True),
            Property(name="is_prose", data_type=DataType.BOOL,
                    skip_vectorization=True),
            Property(name="date", data_type=DataType.TEXT,
                    skip_vectorization=True),
            Property(name="intro", data_type=DataType.TEXT,
                    tokenization=Tokenization.WORD),
            Property(name="excerpt", data_type=DataType.TEXT,
                    tokenization=Tokenization.WORD),
            Property(name="license", data_type=DataType.TEXT,
                    skip_vectorization=True),
            Property(name="notes", data_type=DataType.TEXT,
                    tokenization=Tokenization.WORD),
        ]
    )
      
    # Read data from CSV
    data = pd.read_csv('commonlit_texts.csv')

    # Convert columns to correct types
    data['grade'] = data['grade'].astype(str)  # Convert float to string
    data['lexile'] = data['lexile'].astype(str)  # Convert float to string
    data['is_prose'] = data['is_prose'].astype(bool)  # Convert float to boolean
    data['genre'] = data['genre'].str.split(',') # Convert genre string to array (assuming genres are comma-separated)

    # Convert data to import
    sent_to_vector_db = data.to_dict(orient='records')
    total_records = len(sent_to_vector_db)
    print(f"Inserting data to Vector DB. Total records: {total_records}")

    # Import data to DB based on batch
    with movie_collection.batch.dynamic() as batch:
        for data_row in sent_to_vector_db:
            print(f"Inserting: {data_row['title']}")
            batch.add_object(properties=data_row)

    print("Data saved to Vector DB")


# Check exist collection
if vector_db_client.collections.exists(COLLECTION_NAME):
    print("Collection {} already exists".format(COLLECTION_NAME))
else:
    create_collection()

vector_db_client.close()