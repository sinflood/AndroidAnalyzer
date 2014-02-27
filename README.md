AndroidAnalyzer
===============
We plan to create a system for automated static analysis on Android APK files. The system will decompile the app back into Java pseudo-source code files. From there we will run an analysis script over the source code to extract relevant features and store the features in a database. We plan to look for features related to three topics: hardcoded credentials, sensitive data transmitted over an unencrypted medium and indicators of application popularity. 

Some relevant parameters to look for include:
- Static final variables that look like hard coded access keys. To do this we plan two tactics:
	-Research the possibility of positively identifying a string as being a key based on knowing the characteristics of three popular keys: AWS, Google Maps and Facebook API key.
	-Search decompiled source for likely variable names: secret, key, password, api, aws, etc.
- key/value pairs from strings.XML
- Locations of http(s) connections.
- Variables referenced in url string
- Lines of code in the application
- Code or UI libraries
- Presence of social media buttons
- Ratio of Lines of UI code to regular LoC

From this data we will quantify the frequency of hardcoded credential vulnerabilities and sensitive information sent over plaintext HTTP. We will also examine features that have a strong correlation with application popularity.
