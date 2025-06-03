import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    books = pd.read_csv('data/Books.csv', low_memory=False)
    ratings = pd.read_csv('data/Ratings.csv', low_memory=False)
    users = pd.read_csv('data/Users.csv', low_memory=False)
    return books, users, ratings

def show_home():
    st.title("📚 Top 50 Popular Books")

    books, users, ratings = load_data()

    # Clean books
    books.dropna(subset=['Book-Title', 'Book-Author', 'Publisher'], inplace=True)

    # Clean users
    users['Age'] = users['Age'].fillna(users['Age'].median())
    users = users[(users['Age'] > 5) & (users['Age'] < 100)]

    # Filter ratings
    ratings = ratings[ratings['Book-Rating'] > 0]

    # Merge
    ratings_with_name = ratings.merge(books, on='ISBN')

    # Calculate popularity
    num_rating_df = ratings_with_name.groupby('Book-Title')['Book-Rating'].count().reset_index()
    num_rating_df.rename(columns={'Book-Rating': 'num_ratings'}, inplace=True)

    avg_rating_df = ratings_with_name.groupby('Book-Title')['Book-Rating'].mean().reset_index()
    avg_rating_df.rename(columns={'Book-Rating': 'avg_rating'}, inplace=True)

    popular_df = num_rating_df.merge(avg_rating_df, on='Book-Title')
    popular_df = popular_df[popular_df['num_ratings'] >= 250].sort_values('avg_rating', ascending=False).head(50)
    popular_df = popular_df.merge(books, on='Book-Title').drop_duplicates('Book-Title')[['Book-Title','Book-Author','Image-URL-M','num_ratings','avg_rating']]

    # Styling
    st.markdown("""<style>
        .book-card {
            margin-bottom: 30px;
            text-align: center;
            padding: 15px;
            background-color: #1e1e1e;
            border-radius: 10px;
            height: 480px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            color: #fff;
            box-shadow: 0 0 10px rgba(0,0,0,0.5);
            transition: transform 0.2s;
        }
        .book-card:hover {
            transform: scale(1.10);
        }
        .book-image-container {
            height: 200px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 10px;
        }
        .book-image {
            max-height: 200px;
            width: auto;
            border-radius: 5px;
            object-fit: contain;
        }
        .book-title {
            overflow: hidden;
            font-weight: bold;
            font-size: 16px;
            color: #ffffff;
            margin: 10px 0;
            line-height: 1.3;
        }
        .book-caption {
            font-size: 14px;
            color: #cccccc;
            margin-bottom: 5px;
        }
        .book-rating {
            font-size: 15px;
            color: #ffdd57;
            font-weight: 600;
        }
        .book-votes {
            font-size: 13px;
            color: #aaaaaa;
            margin-top: 3px;
        }
    </style>""", unsafe_allow_html=True)

    for i in range(0, len(popular_df), 4):
        cols = st.columns(4)
        for j, (_, row) in enumerate(popular_df.iloc[i:i+4].iterrows()):
            with cols[j]:
                st.markdown(f"""
                    <div class='book-card'>
                        <div class='book-image-container'>
                            <img class='book-image' src='{row["Image-URL-M"]}'/>
                        </div>
                        <div class='book-title' title='{row["Book-Title"]}'>{row["Book-Title"]}</div>
                        <div class='book-caption'>by {row["Book-Author"]}</div>
                        <div class='book-rating'>⭐ {row["avg_rating"]:.1f}</div>
                        <div class='book-votes'>({row["num_ratings"]} votes)</div>
                    </div>
                """, unsafe_allow_html=True)

if __name__ == '__main__':
    show_home()
