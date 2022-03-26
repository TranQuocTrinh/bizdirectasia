# Keyword Extraction

## Content
We use requests and BeautifulSoup to get the content from a URL.

## Summary
We use the model `KeywordExtractor` to extract keywords from the content.

## Analysis
We use analyze_text_syntax api from google cloud natural language to get the syntax of the content.

## Noun Phrase Extraction
From result of analyze_text_syntax, we extract noun phrases