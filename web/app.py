# import os
# from dotenv import load_dotenv
from web import create_app
#load_dotenv()
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5097)
    # app.run(
    #     host=os.getenv('FLASK_HOST', '0.0.0.0'),
    #     port=int(os.getenv('FLASK_PORT', 5097)),
    #     debug=os.getenv('FLASK_ENV') == 'development'
    # )