# Major prompts for the AI-Driven Development

## v0.1 [2024-12-13]

You're an expert mobile app developer. The final goal is to create a **Native Mobile App** that crafts cutting-edge nutricional advices for users based on their health data, gathered primarily from their Apple, Garmin and Polar Watches. This project will highly likely be large, so we'll firstly create a prototype, that is, a draft, refining it time by time.

1. Inner technical details.
    1.1. Mobile OS: according to the data shown in the website `https://gs.statcounter.com/android-version-market-share/mobile-tablet/worldwide/#monthly-202311-202411-bar`, between the date range between November 2023 and November 2024, there are two OS that stand out from the rest: Android and iOS (iPadOS included), with a 71.21% and 28.14% market shares, respectively. Then, the app will be developed for both of them.
    1.2. OS versions
        1.2.1. Android (mobile and tablet). According to the website `https://gs.statcounter.com/android-version-market-share/mobile-tablet/worldwide/#monthly-202311-202411-bar`:
            - In the date range between November 2023 and November 2024, the most popular Android version is Android 13, with a 25.37% market share, above Android 14. The latter was released in October 2023, but even having passed a year, it's still not the most popular version, which suggests buggy and/or unstable performance.
            - The minimum acceptable version is Android 10 with a 7.95% market share, but if we encounter any compatibility issues as we develop the app, we'll accept Android 11 as the minimum acceptable version with 14.72% market share.
            - As of November 2024, Android 14 is the most popular version with a 36.47% market share, above Android 13 with a 18.73% market share, but because we seek durability, we will rely on the date range between November 2023 and November 2024.
        1.2.2. iOS. According to the website `https://gs.statcounter.com/ios-version-market-share/mobile/worldwide/#monthly-202311-202411-bar`:
            - In the date range between November 2023 and November 2024 the most popular iOS version is not the most recent version 18, but iOS 17.5 with 14.5% market share, released in September 2023, above version 17.6 with 11.3% market share. What's more, As of November 2024, the most popular iOS version is 17.6 with 37.94% market share. It's surprising taking into account how fast people upgrade their phones. More complete data is available via a CSV file.
            - If we take into account what iOS versions are currently supported in `https://en.wikipedia.org/wiki/IOS_version_history` and apply to the plot at file @~/downloads/ios_version-ww-monthly-202311-202411_versions_numbers.png, we can confirm that the most recent versions are not the most used ones, but version 17.5 with 14.19% market share, above version 17.6 with 11.3% market share and way above 17.7 -the last in series 17- with just a 0.77%. Version 17.0 is still supported but with only 1.96% market share, and the next one, 17.1, with 8.47% market share.
            - In order to be future-proof, we'll accept iOS 17.1 as the minimum acceptable version.
        1.2.3. iPadOS. According to the website `https://gs.statcounter.com/ios-version-market-share/mobile-tablet/worldwide/#monthly-202311-202411-bar`: the situation is very similar to iOS regarding the periods November 2023 and November 2024, as well as only November 2024.
            - In the first period, iPadOS 17.5 is the most popular version with a 12.23% market share, above iPadOS 17.6 with a 9.49% market share.
            - According to the detailed statistics at file @~/downloads/ipados_version-ww-monthly-202311-202411_versions_numbers.png, the most popular version is iPadOS 17.5 with a 12.23% market share, above iPadOS 17.6 with a 9.49% market share, and way above iPadOS 17.7 -the last in series 17- with just a 0.91%. Again, we encounter that version 17.0 is still supported but with only 0.73% market share, and the next one, 17.1, with 6.29% market share. In order to be future-proof, we'll accept iPadOS 17.1 as the minimum acceptable version.
            - As of November 2024, iPadOS 17.6 is the most popular version with a 35.44% market share.
            - Then, the minimum acceptable version is iPadOS 17.1.
    1.3. Watches:
        - The analysis of popular sports watch brands and firmware trends (see file @~/downloads/worldwide_watch_brand_popularity.png) reveals Apple, Garmin, Samsung, and Fitbit dominate the global market for sports and fitness watches, with Apple leading at 21% market share. Garmin follows with 17%, Samsung at 12%, and Fitbit at 10%, while other brands collectively account for 40% of the market. These four brands represent the primary focus for development due to their widespread adoption and ecosystem maturity.

        - To ensure broad compatibility and user adoption, we'll develop mechanisms that allow data collection for the following brands and firmwares:

        1. Apple: watchOS Series 9 and 10.
        2. Garmin: Q4 (minimum requirHed), Q3, Q2, and Q1 (latest).
        3. Samsung: Wear OS 4 and Wear OS 5 (current).
        4. Fitbit: firmwares from 210.21 to 210.26 (latest)

    2. Backend:
        2.1. Database: because of my lack of experience with the watches, I don't know what DB would suit best, so I'll let you decide which to use for each platform (i.e. Android, iOS and iPadOS), based on your knowledge.
        2.2. Language: the mechanism involves data collection and analysis. Even if I don't expect that analysis to be exhaustive and to build nutritional advices, it will be more on relying on scientific research and/or expert advices, in principle I'll choose:
            2.2.1. Android, iOS and iPadOS: Python (my strongest skills at programming on it) for the backend.
            2.2.2. iOS-first: Swift (server-side)
            2.2.3. Android-first: Java
    3. Frontend: the idea is to create a mechanism that will be able to gather data from the watches and store it in a database. Because the app will be native, I'll choose:
        3.1. iOS and iPadOS: SwiftUI
        3.2. Android: XML layouts. AI-based suggestions also included Jetpack Compose as I'm writing this file, I don't know what's best to suit the overall project.
2. Data collection and management
    - The following will be done in the `Physical Settings` menu.
    2.1. Anthropometric data: in the initial stage, the app will ask the user for their anthropometric data:
        2.1.1. Height
        2.1.2. Weight
        2.1.3. Date of birth
        2.1.4. Gender (male or female)
        2.1.5. Physical activity level
            - Sedentary (0 h/week)
            - Occasional (0-1 h/week)
            - Regular (1-3 h/week)
            - Moderate (3-5 h/week)
            - Intense (more than 5-8 h/week)
            - Semi-professional (8-12 h/week)
            - Professional (more than 12 h/week)
        2.1.6. Dietary preferences:
            - Vegan
            - Vegetarian
            - Pescatarian
            - Flexitarian
            - Omnivore
        2.1.7. Usual meal times (non-strict):
            - Breakfast
            - Lunch
            - Dinner
            - Snacks: let the user multiple choice which meals it wants to have snacks between.
        - The user can have health issues or have its own preferences, like intermittent fasting, etc, so we will firstly let the user choose what meals wants to have (via checkboxes).
        - All this data will be used to consult to the online scientific literature to provide the user with a personalised nutritional advices.
        - Nevertheless, the user will be able to change their data at any time, and the app will be able to update the nutritional advices accordingly.
    2.2. Activity data: the data will be collected from the watches, stored in a database and processed by the backend. When the user triggers the synchronisation mechanism, the app will ask for the data from the watches and store it in the database.
    2.3. Cooking material:
        2.3.1. Some dishes might be difficult to cook or be more elaborated than normal, so it's necessary to create an AI-based scientific literature consulting mechanism to create another database of cooking procedures. In principle, this will be updated every once in three-four months automatically.
        2.3.2 **Purpose (INTERNAL, DO NOT CODE NOTHING RELATED TO THIS FOR NOW)**
            - The above will be used to consult with our chef so that he or she **prepares videos explaining how to cook the dishes** and upload them in the database. **I'll check it internally about how the chef can upload the videos to the database. The videos will be similar to Instagram reels or TikTok shorts, so that the user doesn't get bored**.
            - Nevertheless, because covering all possible dishes would required a fantastic effort and to avoid overloading the chef, we will try to cover the most popular or common dishes, and limit the number of videos to upload to this database.l
            - **The videos won't neither be downloadable nor shareable accross social media**.
3. Data processing:
    3.1. The data will be processed by the backend (remember the point 2; the backend will be chosen based on the platform, i.e. Android, iOS and iPadOS). The processing manner will depend on the scientific literature, which I expect to have mathematical, statistical and/or physiological models that will serve from data. Relevant models will be chosen, and the data stored in the database will be processed such that it can be used as the input for the models.
4. Data output:
    4.1. Based on the data stored in the database and the model outputs, the app will build a file with a personalised weekly nutritional menu or plan.
        4.1.1. Format: the output will be in JSON, to then be converted to PDF format.
        4.1.2. Date range:
            - It will cover a week starting on Monday and ending on Sunday.
            - Format: the Python f-string f"From {%A1 %Y1-%m1-%d1} to {%A2 %Y2-%m2-%d2}".
            - The date range itself will be the subtitle of the PDF file.
        4.1.3. The file will have the following content for each day:
            - Breakfast
            - Lunch
            - Dinner
            - Snacks (remember what meals the user wants to have snacks between)
        4.1.4. Possible difficult or elaborated dishes
            - We will take into account the database of the cooking procedure videos (point 2.3).
            - If any difficult or more elaborated dishes, these will be lunches and or dinners, so at the left of the text that describes the dish, there will always be a `How to cook` button. This button will be a link to the video in the database, and it'll open a window to reproduce the video.
        4.1.5. `Reasons for the menu tailorings` section:
            - This will be a section header at the very bottom of the file.
            - AI-driven mechanisms will explain the reasons for the menu tailorings and the information will be written below the section header.
        4.1.6. Cooking bills:
            - The app will perform a search in the nearest supermarkets to the user's location, and it will show the total price of the entire meal in euros, at the right side of the name of the meal (i.e. {breakfast, lunch, dinner, snacks}).
            - The app will be able to generate a bill for the cooking of the dishes, with the price of the ingredients and the time it takes to cook each dish.
    4.2. Refining data output:
        - Although AI-driven mechanisms do take into account the dietary preferences, the user might still want to refine and/or correct the menu tailorings, due to particular preferences or health issues (e.g. gluten or lactose intolerant, diabetic, etc.).
        - To take them into account, in the `How to cook` section, below the reproduction area, there will be a text input field with the default text "Write a comment about the dish" (light grey colour). Comments or suggestions may be written in this input field.
        - Then, the app will use the same mechanism to generate the weekly menu, but particularly for writing notes about how can the user achieve the desired results. These notes will appear below the text input field. The app will consider these notes to recalculate the billing of the entire meal and show this updated value at the right side of the name of the meal (i.e. {breakfast, lunch, dinner, snacks}).
    4.3. File processing options.
        - Once the file is processed, two buttons will appear:
            - `Open menu`: display the PDF formatted file.
            - `Download`: open the default file browser of the cellular device, but show the `downloads` directory as the default directory. I think all modern iOS and Android devices have this directory. Maintain all `How to cook` buttons and all the links to the videos.
5. Notifications:
    5.1. Based on the meal times specified at point 2.1.7, the app will send UI notifications to the user at the specified times.
    5.2. The text of the notifications will be randomly chosen from the following set:
        - "It's time for {breakfast, lunch, dinner, snacks}! Check your menu for today."
        - "Have you already eaten your {breakfast, lunch, dinner, snacks}? Take a look at your menu for today."
        - "Don't forget to eat your {breakfast, lunch, dinner, snacks}! Here's what you have for today."
        - "I have a delicious {breakfast, lunch, dinner, snacks} for you! Check it out."
        - "Ready for your {breakfast, lunch, dinner, snacks}? Then forget the rest and come see what you have for today."
            - The brackets indicate all possible meals. It will be substituted by the actual meal name.
    5.3. Redirection to the menu:
        5.3.1. If the user clicks on the notification, the app will open and redirect to the menu: that of the day with all meals and, below, the meal in turn, with the `How to cook` button.
        5.3.2. If the user opens the app by clicking the app icon, the app will show the initial screen (i.e. start normally) but showing the text message of the point 5.2, and a button to redirect to the same info as in point 5.3.1 (`How to cook` button included).
6. Check the user is complying with the menu:
    6.1. When the user gets to the menu by means of the point 5.3.1 or 5.3.2, apart from all visible info and buttons, there will be:
        6.1.1. An additional message that will say "Come on, let me see if you're doing well by taking a photo of your meal".
        6.1.2. Below it, a button with the camera icon that opens the camera (choose the appearance you want for it, we'll refine it in the next versions).
        6.1.3. That photo will be processed by the chosen model for image detection, and it will compare the menu in turn (the text) with the photo.
            - We'll consider a pass if the similarity is above 75%.
            - If a pass, a message will appear saying "You're doing well, enjoy your meal!".
            - If a fail, a message will appear saying "Alright, I know the meal looks tasty, but keep in mind that you're not eating the same as your menu! Take it into account for next time!".
    6.2. Exceptions.
        - There can be times in which the user is travelling and/or having any meal outside the home, or even not wanting to eat because of some health issues or emotional breakdowns.
            6.2.1. Skip a meal
                - Place a button saying "Skip" at the right side of the info screen at point 5.3.
                - When the user clicks it, show a calming message saying "I'm sorry to hear that, but I hope you'll have a good meal anyway! Keep positive!". Skip will only be available if the user is at home.
            6.2.2. Tell the app the user is not at home
                - Place a button just below the "Skip" button saying "Not at home".
                - When the user clicks it, the app will ask to take a photo of the printed menu: button "Take photo of the menu"
                - Alternatively, if not available, the user can upload any file that contains the menu, be it a PDF, a JPG, a PNG, etc. Of course, screenshots are allowed. The button will be "Upload file", below the "Take photo of the menu" button.
                - The photo or file will be processed by the chosen model for image detection, and it will compare the menu in turn (the text, given by the app) with that photo or file.
                - The output will be a message with the following structure:
                    - Introductory message saying "Alright, so you're not at home, but I've found a suitable choice for you!".
                    - Pick up the dishes of the restaurant menu so that they're as similar as possible to the recommended by the app.
                    - If the photo is blurry, ask the user to take a better photo.
                    - If not, but the model cannot find any suitable dish, make the model retry automatically, trying with less suitable dishes at a time. If this is the case, make the model print a message indicating that it's trying with less suitable dishes.
                    - When done, print a message saying what dishes should be chosen.
                    - If by any means the model cannot find any suitable dish, print a message saying "I'm sorry, but I cannot find any suitable dish for you. Lucky of you, eat what you want, but keep in mind that you're not eating healthy!". Then, the entire meal will be considered as "User preferred".
            6.2.3 After having solved the exception:
                - The app will ask the user to take a photo of the dishes set at point 2.1.7. The user can take a photo of the dishes when they're ready to eat, it's not necessary to wait until all the dishes are in the table.
                - The photo will be processed by the chosen model for image detection, and it will compare the menu in turn (the text, given by the app) with each photo.
                - We'll consider a pass if the similarity is above 75%.
                - If a pass, the app will show a message saying "You're doing well, enjoy your meal even if you're not at home!".
                - If a fail, the app will show a message saying "Alright, I know the meal looks tasty, but keep in mind that you're not eating the same as your menu! Take it into account for next time!".
        - In either case, the app will count the skipped meals or days in which the user is not at home for statistical purposes.

7. Historical records.
    7.1. Storage: a database table with the following columns:
        7.1.1. Date: the day, in the Pythonic format f"{%A %Y-%m-%d}".
        7.1.2. Meal: {breakfast, lunch, dinner, snacks}
        7.1.3. Dish (each for the corresponding same meal):
            - If the user is at home (i.e. not clicked on "Not at home" button), the name of the dish.
            - If not, the recommended dish by the app. If no suitable dish is found, the value will be "User preferred".
        7.1.4. Similarity percentage: the percentage of similarity between the dish and the photo. Mark it as 0 if the dish value is "User preferred".
    7.2. Every time the process at point 6 is completed, the info gathered at point 7.1 will be stored in the database table as a single entry.
    7.3. Showing the statistics to the user:
        7.3.1. There will be a button at the home screen saying "Statistics".
        7.3.2. When the user clicks it, the app will show several graphs for all days of a month, either in bar format or in line format (the user can choose the format).
            - The X-axis will be grouped by days, in which each day will contain the labels of the meals.
            - The Y-axis will be the similarity percentage.
            - If the single meal was done at home, the bar or line will be green.
                - If any meal skipped, the bar will be yellow-green.
            - If the single meal was done outside home, the bar or line will be maroon.
                - In this case, if the entire meal happens to be "User preferred", the bar will be red.
        7.3.4. Below the graphs, the following numerical information will be shown:
            - Total number of days of month in which the user is at home and outside it.
            - Total number of skipped meals in the current month, discerned by meal.
            - Monthly average of similarity percentages, discerned by meal.
            - Number of passes and fails, discerned by meal.
8. AI-based processing, guidance and suggestions:
    8.1. The LLMs that will take care of gathering data from the watches, processing it, finding the best advices and outputting them in a structured format will be:
        8.1.1. GPT-4o
        8.1.2. Claude 3.5 Sonnet
        8.1.3. Claude 3.5 Opus
        8.1.4. Claude 3.5 Haiku.
        - We'll set the model 8.1.1. on by default.
    8.2 For image processing, the model set will be:
        8.2.1. **CLIP (Contrastive Language-Image Pretraining)** by OpenAI: This model is highly popular for image-text similarity. It creates embeddings for both images and text, allowing for robust comparisons in a shared latent space. CLIP supports zero-shot learning, meaning it works well without needing task-specific fine-tuning.
        8.2.2. **Emu2**: A unified multimodal framework available on Hugging Face, Emu2 excels in tasks like image captioning, text-to-image generation, and image-text correspondence. It can adapt to various domains with fine-tuning, making it versatile.
        8.2.3. **IDEFICS (Image-aware Decoder Enhanced)**: Inspired by DeepMind's Flamingo model, IDEFICS handles image-text tasks, such as visual content description and image-based Q&A. It’s known for its large-scale training on publicly available datasets.
        8.2.4. **Fuyu-8B**: A compact and efficient model tailored for image understanding tasks like image captioning and visual question answering. It performs well even on resource-limited devices.
        8.2.5. **Nomic Embed Vision**: A lightweight model ideal for embedding both text and images into a multimodal space. It’s designed for semantic search across datasets and achieves high benchmarks in multimodal applications.
        - We'll set the model 8.2.1. on by default.
    8.3. In either case, I prefer not sticking to a single model, as it might suffer from slow server responses, unexpected errors and maintenance notices, or even provide slightly nonsensical pieces of advices. The user will be able to choose the model it prefers via settings, and the app will be able to switch between them if one of them is down.
9. Project tree structure: taking into account the previous points, create a project tree structure, both files and directories. Give a cool name to the root directory.

---

## v0.2 [YYYY-MM-DD]