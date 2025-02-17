# Steps to Create a Reddit App:
# Log in to Reddit:
# Go to Reddit's App Preferences.
# Create a new app:
# Scroll down to "Developed Applications" → Click "Create App".
# App Type: Choose "script" (since this is for personal use).
# Name: Give your app a meaningful name (e.g., "Crowd Helper Bot").
# Redirect URI: Set it to http://localhost:8000 (you don’t need this for scripts, but Reddit requires a value).
# Click "Create App".
# Get Your Credentials:
# After creating, you’ll see a section with:
# Client ID (Found under "personal use script").
# Client Secret (Found under "secret").
# User Agent (Any descriptive name like "myRedditBot:v1.0 (by u/YourRedditUsername)").



import praw

def crowd_solve_reddit(issue):
    # Set up the Reddit client using your app credentials
    reddit = praw.Reddit(
        client_id="YOUR_CLIENT_ID",
        client_secret="YOUR_CLIENT_SECRET",
        user_agent="YOUR_USER_AGENT"
    )

    # Search for relevant posts in a specific subreddit (e.g., r/techsupport)
    subreddit = reddit.subreddit("techsupport")
    results = subreddit.search(issue, limit=5)  # Get the top 5 posts

    suggestions = []
    for post in results:
        suggestions.append(f"💡 {post.title}: {post.url}")

    if not suggestions:
        return f"🚨 No suggestions found for issue: '{issue}' on Reddit."

    return f"👥 Reddit Suggestions for issue: '{issue}':\n" + "\n".join(suggestions)

# Example usage
issue_description = "How to fix slow internet?"
print(crowd_solve_reddit(issue_description))



