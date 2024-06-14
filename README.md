# ![FC_logo](https://github.com/FrackOverflow/FollowerCenobite/blob/main/ProgramData/Images/fc_logo.svg) FollowerCenobite
FollowerCenobite is gives a detailed view of Instagram data over time. FC is not a bot, it consumes JSON data about follows/likes and allows you to drill down and see your relationship with users across multiple accounts.

FC is currently under construction!!! To contribute see [contributing](https://github.com/FrackOverflow/FollowerCenobite/blob/main/Docs/Contributing/Contributing.md)

## The Main Idea
Growing an instagram following requires managing a lot of relationships. After unfollowing one of my friends one too many times I decided to make FC. FC is a relationship manager, not a bot, an automated crawler, or anything that might get you banned. It doesn't even interact with Instagram (though some small interactions are planned on the roadmap).

FC focuses on publicly available information, you don't need to own the instagram account you are analyzing. However if you do decide to collect information for FC, its recommended that you don't do it from the account you are analyzing, or any other account linked to it. I have never run into trouble but even better if you can't be traced at all :)

## Roadmap
0. Json Import UI
1. Dark mode UI should use dark grey + less bright white
    - Fix light mode icons
    - Update Style guide colors
2. Write DB Class Tests
3. Implement Follow/Unfollow Crawler
4. Crawler UI
5. Exclusion lists!
6. Follow/Unfollow Crawler Tests (Including tests for Json consumption)
7. User Detail Page
8. Import Rollback
9. Rollback tests
10. Cannabalize User's Followers
11. Integrate JSON collection
12. Warning window is cluttered
13. Setup window should either be a single window w 2 inputs, or just username entry and set abbreviation later.

## Completed
1. DB Design
    - DB Tables
    - DB Model Classes
    - DB Connection & Query classes
    - DB Auto-init
2. Setup UI
3. Updated UI from PySimpleGUI to CustomTKinter
4. Redid Setup UI
5. Created Style Guide
6. Updated all files to match style guide
7. Removed PySimpleGUI data/classes from model
8. Main UI window/navigation
9. Designed logo and replaced stock images
10. Finished contribution startup guide
11. Add License

# Attribution
FC Logo by FrackOverflow  
Icons by svgrepo.com  
