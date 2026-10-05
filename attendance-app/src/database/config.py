import streamlit as st


from supabase import create_client, Client

supabase: Client = create_client(
    "https://tyfxobwrywztylxoiaui.supabase.co",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR5ZnhvYndyeXd6dHlseG9pYXVpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTExODQ4NjUsImV4cCI6MjEwNjc2MDg2NX0.FphRiyOVOpruKfXrLMRJqBXWGxVE6XNZPEp6kFKXgeE"
)