<div align="center">
  <h1> 🧱 brickseek-scraper </h1>
  <p>🐍A Python program that uses Selenium to automatically scrape all Brickseek.com Walmart clearance deals within a specified search radius. </p>
</div>

## 🎯 Features
- Automatically exports markdowns to .csv file
- Filter markdowns by category
- Filter markdowns by percent off
- Filter markdowns by dollars off
- Configurable search radius

## 📝 Requirements
- Brickseek.com Premium Membership
- Python 3.7 or newer
- Google Chrome
- ChromeDriver downloaded
#### You can download the chrome driver at this [link](https://chromedriver.chromium.org/downloads)
  - ⚠️ Make sure to get the version that matches your current browser version for Chrome.
  - ⚠️ Place the chromedriver.exe file in your project directory and Selenium will automatically find it

## ⚡ Quick Setup Guide
1. Clone this GitHub repo:
    ```
    git clone https://github.com/austinmp/brickseek-scraper.git
    ```
2. Place the chromedriver.exe file in your project directory.
3. Run this command within your project directory to install project dependencies :
     ```
     pip install -r requirements.txt
     ```
4. Create a .env file within your project directory with the following variables
    ```
    BRICKSEEK_USERNAME=yourBrickseekUsername
    BRICKSEEK_PASSWORD=yourBrickseekPassword
    BRICKSEEK_ZIPCODE=01002 
    BRICKSEEK_RADIUS=15
    ```
   > The above configuration will search all Walmart clearance deals within a 15 mile radius of the 01002 zip code.
   
5. To start scraping run:
     ```
     py brickseek.py
     ```
     
## 👨‍💻 Author
Austin Pinto
