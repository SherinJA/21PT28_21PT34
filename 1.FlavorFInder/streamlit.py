import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.multioutput import MultiOutputClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.metrics import accuracy_score

def main():
    page_bg_img = """
    <style>
    [data-testid="stAppViewContainer"]
    {
    background-image: url("https://woodstockfarmersmarket.com/wp-content/uploads/2023/01/WFM-_-Pattern-Background-1024x438.png");
    background-size: cover;
    }

    [data-testid="stAppViewContainer"]{
    background-color:rgba(0,0,0,0);
    }

    .stButton>button {
    background-color: rgb(149, 69, 53);
    color: #ffffff; /* Text color */
    font-weight: bold;
    font-size: 16px; /* Increase font size */
    border: 2px solid rgb(149, 69, 53);
    border-radius: 10px;
    padding: 10px 20px;
    }

    .stButton>button:hover {
    background-color: #ffd700; /* Yellow on hover */
    color: #000000; /* Text color */
    }

    .yellow-button {
    background-color: #ffd700 !important; /* Yellow */
    color: #000000 !important; /* Text color */
    }
    </style>
    """

    st.markdown(page_bg_img, unsafe_allow_html=True)

    st.title("FlavorFinder")


    # Dropdown menu
    cooking_methods = [
    "Deep-frying",
    "Boiling",
    "Stir-frying",
    "Blending",
    "Baking",
    "Freezing",
    "Steaming",
    "Distillation",
    "Grilling",
    "Roasting",
    "Assembling",
    "Sun-frying",
    "Frying"
    ]

    if "page" not in st.session_state:
        st.session_state.page = 0

    def nextpage(): st.session_state.page += 1
    def restart(): st.session_state.page = 0

    

    if st.session_state.page==0:
        st.session_state.user_input = st.text_input("Enter an Indian food:")
        st.session_state.option = st.selectbox("Select cooking method:", cooking_methods)
        st.write("Choose ingredients")
       

        if 'selected_ingredients' not in st.session_state:
            st.session_state.selected_ingredients = []

        important_ingredients = [
            "Salt", "Sugar", "Oil", "Flour", "Milk",
            "Egg", "Butter", "Garlic", "Onions", "Tomato"
        ]

        num_cols = 3
        cols = [st.columns(num_cols) for _ in range((len(important_ingredients) + num_cols - 1) // num_cols)]

        idx = 0
        for row in cols:
            for col in row:
                if idx < len(important_ingredients):
                    ingredient = important_ingredients[idx]
                    if col.button(ingredient, key=ingredient):
                        if ingredient not in st.session_state.selected_ingredients:
                            st.session_state.selected_ingredients.append(ingredient)
                    idx += 1

        new_ingredient = st.text_input("Enter an ingredient:")
        if st.button("Add +"):
            if new_ingredient:
                st.session_state.selected_ingredients.append(new_ingredient)

        if st.session_state.selected_ingredients:
            st.markdown("<h3 style='color:white;'>Ingredients:</h3>", unsafe_allow_html=True)
            for ingredient in st.session_state.selected_ingredients:
                st.markdown(f"<p style='color:white;'>{ingredient}</p>", unsafe_allow_html=True)

    elif st.session_state.page==1:
        st.sidebar.title("Indian food item")
        st.sidebar.write(st.session_state.user_input)
        st.sidebar.title("Selected Ingredients")
        for ingredient in st.session_state.selected_ingredients:
            st.sidebar.write(ingredient)

        st.sidebar.title("Cooking method")
        st.sidebar.write(st.session_state.option)


        submitted_ingredients = st.session_state.selected_ingredients


        print( "final:", submitted_ingredients )


        df = pd.read_excel("food_item_data.xlsx")

        num_categorical_cols = df.select_dtypes(include=['object']).shape[1]
        num_numerical_cols = df.select_dtypes(exclude=['object']).shape[1]

        imputer = SimpleImputer(strategy="most_frequent")

        df.replace('nan', np.nan, inplace=True)

        df_filled = pd.DataFrame(imputer.fit_transform(df), columns=df.columns)

        df_cleaned = df_filled.drop_duplicates()

        df_cleaned.isnull().sum()

        categorical_cols = ['diet', 'flavor_profile', 'course', 'region', 'meal type', 'nutrition quality',
                            'pregnancy-friendly', 'diabetic-friendly', 'cooking method']

        encoding_mappings = {}

        encoder = LabelEncoder()
        for col in categorical_cols:
            df_cleaned[col] = encoder.fit_transform(df_cleaned[col])
            encoding_mappings[col] = dict(zip(encoder.classes_, encoder.transform(encoder.classes_)))


        df_cleaned['state_encoded'] = encoder.fit_transform(df_cleaned['state'])
        df_cleaned.drop(columns=['state'], inplace=True)

        num_categorical_cols = df_cleaned.select_dtypes(include=['object']).shape[1]
        num_numerical_cols = df_cleaned.select_dtypes(exclude=['object']).shape[1]

        additional_label_cols = ['name', 'ingredients', 'cooking method']

        encoder = LabelEncoder()
        for col in additional_label_cols:
            df_cleaned[col] = encoder.fit_transform(df_cleaned[col])

        target_variables = ['diet','region', 'meal type', 'nutrition quality','pregnancy-friendly', 'diabetic-friendly']

        y = df_cleaned[target_variables]
        X = df_cleaned[['name','ingredients','cooking method']]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

        model = MultiOutputClassifier(RandomForestClassifier())

        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)

        for i, target_variable in enumerate(target_variables):
            accuracy = accuracy_score(y_test[target_variable], y_pred[:, i])
            print(f"Accuracy for {target_variable}: {accuracy}")

        new_lis=""

        for word in submitted_ingredients:
            new_lis+=word+','+' '
        
        print("new_lis: ",new_lis)

        new_lis=new_lis[:-2]
        print(new_lis)

        dish_name=st.session_state.user_input
        new_df = pd.DataFrame({
            'name': [dish_name],
            'ingredients': [new_lis],
            'cooking method': [st.session_state.option]
        })

        new_df_cleaned = new_df.drop_duplicates()

        print(new_df)

        new_df_cleaned.isnull().sum()
        test_col=['name','ingredients','cooking method']

        encoder = LabelEncoder()
        for col in test_col:
            new_df_cleaned[col] = encoder.fit_transform(new_df_cleaned[col])

        new_predictions = model.predict(new_df_cleaned)
        print("preds:",new_predictions)

        output_lis=[]

        for i in range(len(new_predictions[0])):
            attribute=target_variables[i]
            if(attribute in list(encoding_mappings.keys())):
                curr_dict=encoding_mappings[attribute]
                for key in curr_dict:
                    if(curr_dict[key]==new_predictions[0][i]):
                        if(attribute=='diabetic-friendly' or attribute=='pregnancy-friendly'):
                            if(key=='Yes'):
                                #print(attribute, end="\t")
                                output_lis.append(attribute)
                        else:
                            #print(key,end="\t")
                            output_lis.append(key)
        
        print(output_lis)
        st.markdown("<h3 style='color:white; text-align: center; font-family: Arial, sans-serif;'>Categories:</h3>", unsafe_allow_html=True)
        for op in output_lis:
            st.markdown(f"<p style='color:rgb(149, 69, 53); font-size: 24px; margin-left: 70px;'>- {op}</p>", unsafe_allow_html=True)

        st.session_state.page=st.session_state.page%2

    st.button("Done",on_click=nextpage,disabled=(st.session_state.page > 1))

        
if __name__ == "__main__":
    main()
