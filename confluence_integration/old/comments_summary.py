page_content = ""
comments = ""

summarize_comments_prompt = f"""
Given the content of a page: 

{page_content}

And the associated comments: 

{comments}

Please provide a summary of the comments with the following considerations:

1. Identify the key themes discussed in the comments.
2. Highlight any new insights or additional information that the comments provide, which are not covered in the page content.
3. Pay attention to any questions raised in the comments and the answers provided.
4. Note any points of agreement or disagreement among the commenters.
5. Summarize these elements concisely to enhance the understanding of the page's content.
"""