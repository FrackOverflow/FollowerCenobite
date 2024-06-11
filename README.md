# FollowerCenobite
FollowerCenobite is gives a detailed view of Instagram data over time. FC is not a bot, it consumes JSON data about follows/likes and allows you to drill down and see your relationship with users across multiple accounts.

FC is currently under construction!!! To contribute see (contributing)[https://github.com/FrackOverflow/FollowerCenobite/blob/main/Docs/Contributing/Contributing.md]

## The Main Idea
Growing an instagram following requires managing a lot of relationships. After unfollowing one of my friends one too many times I decided to make FC. FC is a relationship manager, not a bot, an automated crawler, or anything that might get you banned. It doesn't even interact with Instagram (though some small interactions are planned on the roadmap).

FC focuses on publicly available information, you don't need to own the instagram account you are analyzing. However if you do decide to collect information for FC, its recommended that you don't do it from the account you are analyzing, or any other account linked to it. I have never run into trouble but even better if you can't be traced at all :)

## Roadmap

0. Make Virtual Environment (go to py v11 for self type-hint)
1. Rework Window data 
    - Probably don't need window subtypes and events stored in DB
    - Store static data in the DB! Storing things like method names sets everything in stone T-T
2. Main UI
3. Json Import UI
4. Write DB Class Tests
5. Implement Follow/Unfollow Crawler
6. Crawler UI
7. Exclusion lists!
8. Follow/Unfollow Crawler Tests
9. User Detail Page
10. Import Rollback
11. Cannabalize User's Followers
12. Integrate JSON collection
13. Warning window is cluttered
14. Setup window should either be a single window w 2 inputs, or just username entry and set abbreviation later.

## Completed Features
1. DB Design
    - DB Tables
    - DB Model Classes
    - DB Connection & Query classes
    - DB Auto-init
2. Setup UI
3. Updated UI from PySimpleGUI to CustomTKinter
4. Redid Setup UI
