# Step 1: Install the required libraries (run this only once)
# pip install transformers torch

from transformers import BartTokenizer, BartForConditionalGeneration

# Step 2: Load the pre-trained BART model and tokenizer
model_name = "facebook/bart-large-cnn"
tokenizer = BartTokenizer.from_pretrained(model_name)
model = BartForConditionalGeneration.from_pretrained(model_name)

def summarize_text(text, max_length=50, min_length=25, do_sample=False):
    """
    Summarizes the input text using the BART model.

    Args:
        text (str): The input text to summarize.
        max_length (int): Maximum length of the summary.
        min_length (int): Minimum length of the summary.
        do_sample (bool): Whether to use sampling for generating the summary.

    Returns:
        str: The summarized text.
    """
    # Tokenize the input text
    inputs = tokenizer.encode("summarize: " + text, return_tensors="pt", max_length=1024, truncation=True)

    # Generate the summary
    summary_ids = model.generate(inputs, 
                                 max_length=max_length, 
                                 min_length=min_length, 
                                 length_penalty=2.0, 
                                 num_beams=4, 
                                 early_stopping=True, 
                                 do_sample=do_sample)

    # Decode the summary tokens back to text
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

# Example usage
if __name__ == "__main__":
    # Input text (can be a long business description or report)
    long_description = """
    Artificial intelligence (AI) is revolutionizing industries by enabling automation, improving efficiency, 
    and driving innovation. Businesses are leveraging AI to analyze large datasets, predict customer behavior, 
    optimize supply chains, and enhance decision-making processes. AI-powered tools such as chatbots, 
    recommendation systems, and predictive analytics are becoming essential for staying competitive in today's 
    fast-paced market. Companies that adopt AI technologies can reduce costs, increase revenue, and deliver 
    better customer experiences. However, successful implementation requires careful planning, investment in 
    infrastructure, and a focus on ethical considerations to ensure responsible AI usage.
    """

    # Generate the summary
    short_summary = summarize_text(long_description)
    print("Summary:", short_summary)


##########################################################3


import torch
from transformers import LongformerTokenizer, LongformerForConditionalGeneration

# Step 1: Load Longformer model and tokenizer
model_name = "allenai/longformer-base-4096"
tokenizer = LongformerTokenizer.from_pretrained(model_name)
model = LongformerForConditionalGeneration.from_pretrained(model_name)

# Step 2: Function to summarize long text
def summarize_long_text(texts, max_input_length=4096, max_output_length=150, batch_size=4):
    """
    Summarizes long input texts using the Longformer model.

    Args:
        texts (list of str): List of input texts to summarize.
        max_input_length (int): Maximum token length for the input text.
        max_output_length (int): Maximum token length for the summary.
        batch_size (int): Number of texts to process in each batch.

    Returns:
        list of str: The summarized texts.
    """
    summaries = []

    # Process texts in batches for better performance
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i + batch_size]

        # Tokenize the batch of texts
        inputs = tokenizer(
            batch_texts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=max_input_length
        )

        # Move inputs to GPU if available
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device)
        inputs = {key: value.to(device) for key, value in inputs.items()}

        # Generate summaries for the batch
        summary_ids = model.generate(
            inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_length=max_output_length,
            min_length=30,
            length_penalty=2.0,
            num_beams=4,
            early_stopping=True
        )

        # Decode the summaries
        batch_summaries = tokenizer.batch_decode(summary_ids, skip_special_tokens=True)
        summaries.extend(batch_summaries)

    return summaries

# Example usage
if __name__ == "__main__":
    # Input texts (can be very long business descriptions or reports)
    long_descriptions = [
        """
        Artificial intelligence (AI) is revolutionizing industries by enabling automation, improving efficiency, 
        and driving innovation. Businesses are leveraging AI to analyze large datasets, predict customer behavior, 
        optimize supply chains, and enhance decision-making processes. AI-powered tools such as chatbots, 
        recommendation systems, and predictive analytics are becoming essential for staying competitive in today's 
        fast-paced market. Companies that adopt AI technologies can reduce costs, increase revenue, and deliver 
        better customer experiences. However, successful implementation requires careful planning, investment in 
        infrastructure, and a focus on ethical considerations to ensure responsible AI usage.
        """,
        """
        Blockchain technology is transforming industries by providing secure, transparent, and decentralized 
        solutions for data management and transactions. It is being used in finance, supply chain management, 
        healthcare, and more. Blockchain ensures data integrity, reduces fraud, and eliminates intermediaries, 
        leading to cost savings and increased trust. Despite its potential, challenges such as scalability, 
        regulatory uncertainty, and energy consumption remain barriers to widespread adoption.
        """
    ]

    # Generate summaries
    short_summaries = summarize_long_text(long_descriptions, max_input_length=4096, max_output_length=150)
    
    # Print the results
    for i, summary in enumerate(short_summaries):
        print(f"Summary {i + 1}:", summary)
