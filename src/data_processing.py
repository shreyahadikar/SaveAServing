import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler

def load_and_preprocess_data(filepath: str):
    """
    Loads raw dataset, cleans date formats, handles categorical encoding,
    and returns processed dataframe alongside metadata encoders.
    """
    df = pd.read_csv(filepath)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by=['restaurant_id', 'item_id', 'date']).reset_index(drop=True)
    
    # Categorical Encodings
    label_encoders = {}
    cat_cols = ['category', 'item_id', 'restaurant_id']
    
    for col in cat_cols:
        le = LabelEncoder()
        df[f'{col}_encoded'] = le.fit_transform(df[col])
        label_encoders[col] = le
        
    return df, label_encoders


def prepare_features_and_split(df: pd.DataFrame, test_start_date='2025-12-01', val_start_date='2025-11-01'):
    """
    Performs strict time-series splitting to avoid lookahead bias.
    - Train: Start to val_start_date
    - Validation: val_start_date to test_start_date
    - Test: test_start_date to End
    """
    # Features strictly available BEFORE daily sales occur
    feature_cols = [
        'category_encoded', 'item_id_encoded', 'restaurant_id_encoded',
        'day_of_week', 'is_holiday', 'temperature', 'rainfall',
        'event', 'promotion', 'price', 'sales_previous_day',
        'sales_7_days_ago', 'rolling_7_day_avg'
    ]
    
    target_col = 'quantity_sold'
    
    train_mask = df['date'] < val_start_date
    val_mask = (df['date'] >= val_start_date) & (df['date'] < test_start_date)
    test_mask = df['date'] >= test_start_date
    
    X_train, y_train = df.loc[train_mask, feature_cols], df.loc[train_mask, target_col]
    X_val, y_val = df.loc[val_mask, feature_cols], df.loc[val_mask, target_col]
    X_test, y_test = df.loc[test_mask, feature_cols], df.loc[test_mask, target_col]
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)
    
    split_data = {
        'X_train': X_train, 'y_train': y_train, 'X_train_scaled': X_train_scaled,
        'X_val': X_val, 'y_val': y_val, 'X_val_scaled': X_val_scaled,
        'X_test': X_test, 'y_test': y_test, 'X_test_scaled': X_test_scaled,
        'feature_cols': feature_cols,
        'df_test': df.loc[test_mask].copy()
    }
    
    return split_data, scaler