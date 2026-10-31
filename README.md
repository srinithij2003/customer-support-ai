# AI Customer Support Assistant

A Streamlit application that predicts support-ticket priority and escalation risk, and uses Retrieval-Augmented Generation (RAG) to find answers in product documentation.

## Features

- Predicts ticket priority: High, Medium, Low, or Urgent.
- Predicts whether a ticket may need human escalation.
- Retrieves relevant passages from product documentation.
- Avoids inventing answers when documentation does not support a response.
- Provides an interactive Streamlit interface.
- Keeps the final decision with a human support agent.

## Technology Stack

- Python
- pandas and scikit-learn
- TF-IDF and Logistic Regression
- Sentence Transformers
- FAISS
- Streamlit
- pytest

## Dataset

The models use the `with_ai` configuration of the Hugging Face support-ticket dataset:

https://huggingface.co/datasets/s2pidape/support-ticket-dataset

The prediction targets are `priority` and `escalated_to_human`.

## Project Structure

```text
customer-support-ai/
├── app.py
├── config.py
├── requirements.txt
├── docs/
├── models/
├── reports/
├── scripts/
├── src/
├── tests/
└── vector_store/
```

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Train and Evaluate

Set the dataset sample size and train the models:

```bash
export MAX_TRAIN_ROWS=500000
python -m scripts.train
python -m scripts.evaluate
```

Evaluation results are saved in `reports/evaluation_report.json`.

## Run the Application

```bash
streamlit run app.py
```

Open the local URL shown in the terminal, usually `http://localhost:8501`.

## Working of the Project

The AI Customer Support Assistant combines Machine Learning and Retrieval-Augmented Generation (RAG) to help support teams analyze customer tickets and provide documentation-based assistance.

1. Ticket Input: The user enters the ticket subject and description through a Streamlit web interface.

2. Data Preprocessing: The system processes the ticket text using TF-IDF and extracts relevant structured features. The preprocessing pipeline prepares the input in the format expected by the trained models.

3. Priority Prediction: A supervised Machine Learning model built using Logistic Regression predicts the ticket priority as High, Medium, Low, or Urgent. The model is trained using labelled support-ticket data.

4. Escalation Prediction: A separate Logistic Regression model predicts whether the ticket may require escalation to a human support agent. Both models provide predictions and associated confidence information where supported.

5. Document Processing: Product documentation in PDF, TXT, or Markdown format is loaded from the docs/ directory. The system extracts the text and divides it into smaller chunks for efficient retrieval.

6. Embedding and Indexing: The Sentence Transformers model all-MiniLM-L6-v2 converts document chunks into numerical embeddings. FAISS indexes these embeddings to support similarity-based retrieval.

7. Information Retrieval: When a ticket is submitted, the RAG pipeline searches the indexed documentation for passages relevant to the ticket or customer question.

8. Response Generation: The system uses the retrieved evidence to provide a suggested support response. If the available documentation does not contain sufficient information, the assistant indicates that it cannot find supporting information instead of inventing product instructions.

9. Results Display: The Streamlit interface displays the predicted priority, escalation result, confidence information, and documentation-grounded response or unsupported-answer message.

10. Human Review: The predictions and suggested responses are intended to support—not replace—the support agent. The human agent verifies the evidence and makes the final decision about ticket priority, escalation, and the response sent to the customer.

Overall, the project I did combines supervised classification for ticket triage with semantic document retrieval for evidence-based support, providing a unified interface for more consistent and efficient customer-support workflows.

## Demonstration Scenarios

1. **Password reset:** Predict priority and escalation, then retrieve password-reset instructions.
2. **Service disruption:** Assess a checkout outage and retrieve relevant troubleshooting or incident guidance.
3. **Unsupported question:** Confirm the assistant says it cannot find supporting information.
4. **Vague ticket:** Submit “It is not working” and review the prediction limitations.

## Run Tests

```bash
python -m pytest -q
```

## Limitations

- The dataset is synthetic, so results may not generalize to real support tickets.
- Priority predictions can confuse similar classes.
- Retrieval quality depends on the quality and coverage of the indexed documentation.
- Confidence scores should not be treated as guaranteed probabilities.
- A human support agent must verify evidence and make the final decision.
