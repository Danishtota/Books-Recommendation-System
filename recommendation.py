import streamlit as st
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

@st.cache_data
def load_data():
    books = pd.read_csv(r'D:\Books-Recommendation-System\data\books.csv', low_memory=False)
    ratings = pd.read_csv(r'D:\Books-Recommendation-System\data\ratings.csv')
    return books, ratings

def show_recommendation():
    st.title("📚 Book Recommendation System")

    books, ratings = load_data()

    books.dropna(subset=['Book-Title', 'Book-Author', 'Publisher'], inplace=True)
    ratings = ratings[ratings['Book-Rating'] > 0]

    ratings_with_name = ratings.merge(books, on='ISBN')

    x = ratings_with_name.groupby('User-ID').count()['Book-Rating'] > 50
    padhe_likhe_users = x[x].index
    filtered_rating = ratings_with_name[ratings_with_name['User-ID'].isin(padhe_likhe_users)]

    y = filtered_rating.groupby('Book-Title').count()['Book-Rating'] >= 10
    famous_books = y[y].index
    final_ratings = filtered_rating[filtered_rating['Book-Title'].isin(famous_books)]

    pt = final_ratings.pivot_table(index='Book-Title', columns='User-ID', values='Book-Rating')
    pt.fillna(0, inplace=True)

    if pt.shape[0] == 0 or pt.shape[1] == 0:
        st.error("📛 Not enough data to calculate similarity. Try reducing filters or check your CSV files.")
        return

    similarity_scores = cosine_similarity(pt)

    def recommend(book_name):
        try:
            index = np.where(pt.index == book_name)[0][0]
            similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:21]

            data = []
            for i in similar_items:
                temp_df = books[books['Book-Title'] == pt.index[i[0]]]
                title = temp_df.drop_duplicates('Book-Title')['Book-Title'].values[0]
                author = temp_df.drop_duplicates('Book-Title')['Book-Author'].values[0]
                img = temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values[0]

                rating_count = final_ratings[final_ratings['Book-Title'] == title]['Book-Rating'].count()
                avg_rating = final_ratings[final_ratings['Book-Title'] == title]['Book-Rating'].mean()

                data.append([title, author, img, rating_count, avg_rating])

            # Sort by avg_rating in descending order (highest rating first)
            data = sorted(data, key=lambda x: x[4], reverse=True)
            return data

        except IndexError:
            st.error(f"Book '{book_name}' not found in the recommendation system.")
            return []

    selected_book = st.selectbox("Choose a book to get recommendations:", pt.index)

    if st.button("Recommend Similar Books"):
        recommendations = recommend(selected_book)

        if not recommendations:
            st.warning("No recommendations found. Try selecting a different book.")
        else:
            st.markdown("""
                <style>
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
                        transition: transform 0.2s;
                        color:#ffff
                        box-shadow: 0 0 10px rgba(0,0,0,0.5);
                        cursor: pointer;
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
                        color: #CCCCCC;
                        margin-bottom: 6px;
                    }
                    .book-rating {
                        font-size: 13px;
                        color: #AAAAAA;
                    }
                </style>
            """, unsafe_allow_html=True)

            for i in range(0, len(recommendations), 4):
                cols = st.columns(4)
                for col_idx, col in enumerate(cols):
                    if i + col_idx < len(recommendations):
                        title, author, img, rating_count, avg_rating = recommendations[i + col_idx]
                        short_title = (title[:60] + '...') if len(title) > 60 else title

                        with col:
                            st.markdown(f"""
                                <div class='book-card' title='{title}'>
                                    <div class='book-image-container'>
                                        <img class='book-image' src='{img}'/>
                                    </div>
                                    <div class='book-title'>{short_title}</div>
                                    <div class='book-caption'>by {author}</div>
                                    <div class='book-rating'>⭐ {avg_rating:.1f} ({rating_count})</div>
                                </div>
                            """, unsafe_allow_html=True)

if __name__ == "__main__":
    show_recommendation()