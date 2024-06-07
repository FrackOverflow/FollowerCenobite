# FollowerCenobite
FollowerCenobite is gives a detailed view of Instagram data over time. FC is not a bot, it consumes JSON data about follows/likes and allows you to drill down and see your relationship with users across multiple accounts.

FC is currently under construction!!! It does not work yet!

## The Main Idea
Growing an instagram following requires managing a lot of relationships. After unfollowing one of my friends one too many times I decided to make FC. FC is a relationship manager, not a bot, an automated crawler, or anything that might get you banned. It doesn't even interact with Instagram (though some small interactions are planned on the roadmap).

FC focuses on publicly available information, you don't need to own the instagram account you are analyzing. However if you do decide to collect information for FC, its recommended that you don't do it from the account you are analyzing, or any other account linked to it. I have never run into trouble but even better if you can't be traced at all :)

## Roadmap
1. Replace PySimpleGUI
2. Rework Window data 
    - Probably don't need window subtypes and events stored in DB
    - Store static data in the DB! Storing things like method names sets everything in stone T-T
3. Redo Setup UI
4. Main UI
5. Json Import UI
6. Write DB Class Tests
7. Implement Follow/Unfollow Crawler
8. Crawler UI
9. Exclusion lists!
10. Follow/Unfollow Crawler Tests
11. User Detail Page
12. Import Rollback
13. Cannabalize User's Followers
14. Integrate JSON collection

## Completed Features
1. DB Design
    - DB Tables
    - DB Model Classes
    - DB Connection & Query classes
    - DB Auto-init
2. Setup UI
