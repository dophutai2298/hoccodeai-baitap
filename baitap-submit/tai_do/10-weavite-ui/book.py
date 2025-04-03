import gradio as gr
import weaviate

vector_db_client = weaviate.connect_to_local(
    # # Update if any changes
    # host="127.0.0.1",
    # port=8080,
    # grpc_port=50051,
    # skip_init_checks=True
)
vector_db_client.connect()

COLLECTION_NAME = "BookCollection"

def search_book(query):
    book_collection = vector_db_client.collections.get(COLLECTION_NAME)
    response = book_collection.query.hybrid(
        query=query, alpha=0.5, limit=10
    )

    html_output = """
    <div style="text-align: center; margin-bottom: 20px;">
        <h3 style="color: #fff; font-size: 28px; font-weight: 700; padding: 10px; border-radius: 8px;">
            Search Results:
        </h3>
    </div>

    <div style="display: flex; flex-wrap: wrap; gap: 20px; justify-content: center;">
    """
    for book in response.objects:
        print(book)
        properties = book.properties
        html_output += f"""
        <div style="flex: 1 1 calc(50% - 20px); max-width: 700px; border: 1px solid #ddd; padding: 15px; 
                border-radius: 8px; background-color: #f9f9f9;">
            <p style='color:#c21b17;font-size:22px;font-weight:600'>{properties['title']}</p>
            <p style='color:#222;font-size:18px;font-weight:500'>by {properties['author']}   -   Genre: {properties['genre']}</p>
            <p style='color:#222;font-size:18px;font-weight:400'>Description: {properties['description']}</p>
        </div>
        """
    return html_output

with gr.Blocks(title="Search books with Vector Database Weavite") as interface:
    gr.Markdown("# Search books with Vector Database Weavite")
    query = gr.Textbox(label="Search...", placeholder="Title, author, description,genre...")
    search = gr.Button(value="Search")
    results_html = gr.HTML()  # Display results with custom styling

    search.click(fn=search_book, inputs=query, outputs=results_html)

interface.queue().launch()