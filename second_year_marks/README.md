To modify course information/expand or extend it for 2nd year you just need to change `src/grade_data.json` (otherwise you need to change references to `* Second Year` to be whatever the new calculator is for).

`src/grade_data.json` is largerly self explanatory, to experiment with it/to see if it's suitable run `yarn serve` and modify it, and you should see the changes reflected.

Pretty much everything which is needed for i.e. a 3rd year calculator is implemented, and it's use is probably in `src/grad_data.json`, except for pass/fail courseworks.
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
