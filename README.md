## a fastapi project focus on using kafka as message passing.


## Installation

### Steps

1. **Clone the repository**:
    
    ```
    git clone https://github.com/your-username/your-repo.git
    cd your-repo
    
    ```
    
2. **create a virtual environment**:
    
    ```
    py -m venv venv
    
    ```

3. **activate virtual environment**:
    
    ```
    venv/Scripts/activate
    
    ```
    
4. **install required libraries**:
    
    ```
    pip install -r requirements.txt
    
    ```
5. **set up environment variables in .env**:
    
    ```
    DATABASE_HOST = "your-mongodb-connection-string"
    DATABASE_NAME = "your-database-name"
    
    ```
6. **run the application**:
    
    ```
    uvicorn app.main:app --reload
    ```