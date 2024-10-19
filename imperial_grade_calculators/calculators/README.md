The JSON files contain the information for calculating grades, they are registered in a fairly obvious way in `App.vue`, at the top in the map and further down for the selection menu.

`src/second_year_grade_data.json` is largerly self explanatory, to experiment with it/to see if it's suitable run `yarn serve` and modify it, and you should see the changes reflected.

Pretty much everything which is needed for i.e. a 3rd year calculator is implemented, and it's use is probably in `src/second_year_grade_data.json`, except for pass/fail courseworks.
This is done by setting `"is_pass_fail": true` for any coursework, as opposed to `"marks": [number]`, i.e.:
```js
  {
    "weight": 0.08333,
    "name": "Group Projects",
    "type": "normal",
    "parts": {
      "Some Group Project": {
        "weight": 1,
        "coursework_weight": 1,
        "courseworks": {
          "Project Work": {
            "weight": 1,
            "is_pass_fail": true
          }
        }
      }
    }
  },
```
