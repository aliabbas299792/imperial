<script>
const query_json_map = {
  "overall_meng_calculator": "./overall_grade_data.json",
  "second_year_marks": "./second_year_grade_data"
};

function get_calc_name() {
  return new URLSearchParams(window.location.search).get("calc") || "overall_meng_calculator"
}

function path_to_data_map() {
  const calc_name = get_calc_name()
  return query_json_map[calc_name] || query_json_map["overall_meng_calculator"];
}

function examinable_module_pass(examinable_module_frac) {
  return examinable_module_frac >= 0.4;
}

function progress_to_MEng(overall_frac) {
  return overall_frac >= 0.6;
}

function format_booleans(bool) {
  return bool ? "True" : "False"
}

const default_text_formatter = (a) => a;

function gen_user_data(components) {
  const local_data = localStorage.getItem(`${get_calc_name()}_user_data`);
  if (local_data) {
    return JSON.parse(local_data);
  } else {
    const user_data = {};
    user_data["optional"] = get_optional_map(components, true);

    for (const component of components) {
      const component_name = component["name"];
      user_data[component_name] = {}
      const parts = Object.entries(component["parts"]);
      for (const [part_name, part_data] of parts) {
        user_data[component_name][part_name] = {}
        const courseworks = Object.entries(part_data["courseworks"] ? part_data["courseworks"] : {})
        const exams = Object.entries(part_data["exams"] ? part_data["exams"] : {})
        for (const [coursework_name] of courseworks) {
          user_data[component_name][part_name][coursework_name] = 'n/a'
        }
        for (const [exam_name] of exams) {
          user_data[component_name][part_name][exam_name] = 'n/a'
        }
      }
    }
    return user_data
  }
}

const PRECISION = 4;

function get_optional_map(components, first_selected_default) {
  for (const component of components) {
    if (component.type == "optional") {
      const entries = Object.keys(component.parts).map(part_name => [part_name, false]);
      entries[0][1] = first_selected_default;
      return Object.fromEntries(entries);
    }
  }
}

export default {
  data() {
    return {
      grade_data: [],
      user_data: gen_user_data([])
    }
  },
  created() {
    this.load_grade_data()
  },
  methods: {
    async load_grade_data() {
      let grade_data_file = path_to_data_map()
      try {
        const module = await import(`${grade_data_file}`);
        this.loaded_data = module.default
        this.grade_data = this.loaded_data["grade_components"];
        this.pass_percent = this.loaded_data["pass_percent"];
        this.progress_to_meng = this.loaded_data["progress_to_meng"]
        this.user_data = gen_user_data(this.grade_data);
      } catch (error) {
        console.error('Failed to load grade data:', error);
      }
    },
    handle_calculator_select(event) {
      const selected_value = event.target.value
      const params = new URLSearchParams(window.location.search)
      params.set('calc', selected_value)
      window.location.href = `${window.location.pathname}?${params.toString()}`
    },
    laboratory_component_pass(lab_component_frac) {
      return lab_component_frac >= this.pass_percent;
    },
    overall_pass(overall_frac) {
      return overall_frac >= this.pass_percent;
    },

    getPC(num) {
      return (num * 100).toPrecision(PRECISION) + "%";
    },
    get_grade(frac) {
      if (frac >= 0.795) return 'A*';
      if (frac >= 0.695) return 'A';
      if (frac >= 0.595) return 'B';
      if (frac >= 0.495) return 'C';
      if (frac >= 0.395) return 'D';
      if (frac >= 0.295) return 'E';
      return 'F';
    },
    format_so_far_output(something, something_so_far, formatter = default_text_formatter, cell = this.calculated_grade_values["__TOTAL__"]) {
      const something_val = cell[something]
      const something_so_far_val = cell[something_so_far]
      return `${formatter(something_val)} (${formatter(something_so_far_val)} so far)`
    },
    format_overall_percentage_output() {
      return this.format_so_far_output("total_pc", "so_far_pc")
    },
    format_overall_grade_output() {
      return this.format_so_far_output("total_grade", "so_far_grade")
    },
    format_component_percentage_output(component_name) {
      return this.format_so_far_output("total_pc", "so_far_pc", default_text_formatter, this.calculated_grade_values[component_name]["__TOTAL__"])
    },
    format_component_grade_output(component_name) {
      return this.format_so_far_output("total_grade", "so_far_grade", default_text_formatter, this.calculated_grade_values[component_name]["__TOTAL__"])
    },
    format_part_percentage_output(component_name, part_name) {
      return this.format_so_far_output("total_pc", "so_far_pc", default_text_formatter, this.calculated_grade_values[component_name][part_name])
    },
    format_part_grade_output(component_name, part_name) {
      return this.format_so_far_output("total_grade", "so_far_grade", default_text_formatter, this.calculated_grade_values[component_name][part_name])
    },
    format_pass_output() {
      return this.format_so_far_output("overall_pass_year", "overall_pass_year_so_far", format_booleans)
    },
    format_progress_MEng_output() {
      return this.format_so_far_output("progress_MEng", "progress_MEng_so_far", format_booleans)
    },
    format_lab_pass_output() {
      return this.format_so_far_output("lab_pass", "lab_pass_so_far", format_booleans)
    },
    format_examinable_pass_output() {
      return this.format_so_far_output("examinable_pass", "examinable_pass_so_far", format_booleans)
    },
    is_selected_module(name) {
      if(!this.user_data['optional']) {
        return true
      }

      // it is a selected module if either it's not an optional module, or is optional and is also selected
      return !(name in this.user_data['optional']) || this.user_data['optional'][name];
    }
  },
  watch: {
    user_data: {
      handler() {
        localStorage.setItem(`${get_calc_name()}_user_data`, JSON.stringify(this.user_data))
      },
      deep: true
    }
  },
  computed: {
    selected_calculator() {
      return get_calc_name();
    },
    calculated_grade_values() {
      const pc_values = {};

      let overall_total = 0;
      let weighted_overall_so_far_marks = 0;
      let overall_so_far_weight = 0;

      let examinable_pass = true;
      let examinable_pass_so_far = true;

      let lab_pass = true;
      let lab_pass_so_far = true;

      for (const component of this.grade_data) {
        const component_name = component["name"];
        pc_values[component_name] = {}

        const parts = Object.entries(component["parts"]);
        let total_component_frac = 0;
        let so_far_part_weight = 0;
        let weighted_so_far_marks_component = 0;

        for (const [part_name, part_data] of parts) {
          if (!this.is_selected_module(part_name)) {
            continue;
          }

          const courseworks = Object.entries(part_data["courseworks"] ? part_data["courseworks"] : [])
          const exams = Object.entries(part_data["exams"] ? part_data["exams"] : [])

          let total_weight = 0;
          let so_far_weight = 0;
          let weighted_user_total_marks = 0;

          const coursework_multiplier = part_data["coursework_weight"] || 0;
          const exam_multiplier = 1 - coursework_multiplier;

          for (const [name, data] of courseworks) {
            const cw_weight = coursework_multiplier * data["weight"] * component["weight"] * part_data["weight"];

            // raw value is either a bool, number or string
            // if it's a string then we just skip the mark, for bool we either do or don't give full weight
            // with number we use it appropriately
            const raw_value = this.user_data[component_name][part_name][name];
            const numeric_value = parseFloat(raw_value);
            if (typeof raw_value == "boolean" || !isNaN(numeric_value)) {
              let val = undefined;
              if (typeof raw_value == "boolean") {
                val = raw_value ? cw_weight : 0;
              } else {
                val = numeric_value;
              }

              if ("marks" in data) {
                weighted_user_total_marks += (val / data["marks"]) * cw_weight;
              } else if (data.is_percent) {
                weighted_user_total_marks += (val / 100) * cw_weight;
              } else {
                weighted_user_total_marks += val;
              }

              total_weight += cw_weight;
              so_far_weight += cw_weight;
            } else {
              total_weight += cw_weight;
            }
          }

          for (const [name, data] of exams) {
            const val = parseFloat(this.user_data[component_name][part_name][name]);
            const ex_weight = exam_multiplier * data["weight"] * component["weight"] * part_data["weight"];
            
            if (!isNaN(val)) {
              if ("marks" in data) {
                weighted_user_total_marks += val / data["marks"] * ex_weight;
              } else {
                weighted_user_total_marks += (val / 100) * ex_weight;
              }
              total_weight += ex_weight;
              so_far_weight += ex_weight;
            } else {
              total_weight += ex_weight;
            }
          }

          const total_frac = weighted_user_total_marks / total_weight;
          const total_pc = this.getPC(total_frac);
          const total_grade = this.get_grade(total_frac);

          let so_far_frac = weighted_user_total_marks / so_far_weight;
          if (so_far_weight == 0) {
            // to avoid divide by zero NaN - in this case the user total should be 0 as well so this shouldn't matter
            so_far_frac = 0;
          } else {
            so_far_part_weight += so_far_weight;
          }

          const so_far_pc = this.getPC(so_far_frac);
          const so_far_grade = this.get_grade(so_far_frac);

          if (exams.length > 0) { // has an exam so is an examinable module
            examinable_pass &= examinable_module_pass(total_frac);
            examinable_pass_so_far &= examinable_module_pass(so_far_frac);
          }

          total_component_frac += total_frac * part_data["weight"];
          weighted_so_far_marks_component += weighted_user_total_marks;

          pc_values[component_name][part_name] = { total_pc, total_grade, so_far_pc, so_far_grade };
        }

        if (so_far_part_weight == 0) {
          so_far_part_weight = 1;
        } else {
          overall_so_far_weight += so_far_part_weight;
        }

        const so_far_frac = weighted_so_far_marks_component / so_far_part_weight;

        const total_pc = this.getPC(total_component_frac);
        const total_grade = this.get_grade(total_component_frac);
        const so_far_pc = this.getPC(so_far_frac);
        const so_far_grade = this.get_grade(so_far_frac);

        if (component["type"] == 'laboratory') {
          lab_pass &= this.laboratory_component_pass(total_component_frac);
          lab_pass_so_far &= this.laboratory_component_pass(so_far_frac);
        }

        overall_total += total_component_frac * component["weight"];
        weighted_overall_so_far_marks += weighted_so_far_marks_component;

        pc_values[component_name]["__TOTAL__"] = { total_pc, total_grade, so_far_pc, so_far_grade };
      }

      if (overall_so_far_weight == 0) {
        overall_so_far_weight = 1;
      }

      const so_far_frac = weighted_overall_so_far_marks / overall_so_far_weight;
      // since "so far" weights are calculated using the "overall weighting", divides
      // the weighted total marks by this to get the fraction of all marks achieved (i.e the so far fraction)

      const total_pc = this.getPC(overall_total);
      const total_grade = this.get_grade(overall_total);
      const so_far_pc = this.getPC(so_far_frac);
      const so_far_grade = this.get_grade(so_far_frac);

      const overall_pass_year = this.overall_pass(overall_total);
      const overall_pass_year_so_far = this.overall_pass(so_far_frac);

      const progress_MEng = progress_to_MEng(overall_total);
      const progress_MEng_so_far = progress_to_MEng(so_far_frac);

      pc_values["__TOTAL__"] = {
        total_pc, total_grade, so_far_pc, so_far_grade, overall_pass_year, overall_pass_year_so_far, progress_MEng,
        progress_MEng_so_far, lab_pass, lab_pass_so_far, examinable_pass, examinable_pass_so_far
      };
      return pc_values;
    }
  },
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto+Serif:opsz,wght@8..144,300&display=swap');

html {
  overflow-x: hidden;
}

* {
  word-wrap: anywhere !important;
  font-family: Arial, sans-serif;
}

body {
  padding: 10px 0px;
  margin: 0;
}

input[type='checkbox'] {
  cursor: pointer !important;
  margin: 5px;
  transform: scale(1.4);
}

.mark-input {
  width: 100%;
  border: 1px solid rgb(176, 204, 255);
  border-radius: 3px;
}

#main {
  margin: auto;
  max-width: 900px;
}

.space {
  border: white !important;
}

table th {
  border: 1px solid black;
  overflow: hidden;
  padding: 10px 5px;
  word-break: normal;
  font-size: large;
  font-weight: bold;
  text-align: left;
  text-decoration: underline;
  vertical-align: top
}

table td {
  font-size: small;
  padding: 10px 5px;
  border: 1px black solid;
}

.component-name :first-child {
  font-size: medium;
  font-weight: bold;
  text-decoration: underline;
  border: 1px black solid;
}

.part-name :first-child {
  font-size: medium;
  text-decoration: underline;
}

.coursework {
  font-style: italic;
}

.exam {
  font-weight: bold;
  font-style: italic;
}

.table_head_floating {
  position: sticky;
  top: 0px;
  background: #445195;
  color: white;
  z-index: 1000;
  outline: 10px solid #445195;
}

.table_head_floating th {
  border: none;
}

.part-grade :first-child {
  border: none;
}

.overall-grade td {
  font-size: large;
  background: rgb(36, 59, 118);
  border: 1px white solid;
  color: white;
}

.checkbox {
  padding: 10px;
  display: inline-block;
  background: #F4F8FA;
  border: 1px solid rgb(176, 204, 255);
  border-radius: 5px;
  margin: 5px;
}

#calculator_selector {
    display: block;
    margin: 10px 0px 20px 0px;
    padding: 10px;
    border-radius: 5px;
}
</style>

<template>
  <div id="main">
    <select id="calculator_selector" v-model="selected_calculator" @change="handle_calculator_select">
      <option value="overall_meng_calculator">Overall MEng Grade Calculator</option>
      <option value="second_year_marks">Second Year Calculator</option>
    </select>
    <table>
      <thead>
        <tr class="table_head_floating">
          <th>Component</th>
          <th>Your mark</th>
          <th>Total mark</th>
          <th>Component weighting</th>
          <th>Overall weighting</th>
        </tr>
      </thead>
      <tbody v-for="component in grade_data" :key="component">
        <tr>
          <td class="space"></td>
        </tr>
        <tr class="component-name">
          <td>{{ component["name"] }}</td>
          <td colspan="2"></td>
          <td>{{ getPC(1) }}</td>
          <td>{{ getPC(component.weight) }}</td>
        </tr>

        <template v-if="component['type'] == 'optional'">
          <tr>
            <td colspan="5">
              <template v-for="(option_checked, option_name) in user_data['optional']" :key="option_checked">
                <div class="checkbox">
                  <input type="checkbox" v-model="user_data['optional'][option_name]" /> <label for="checkbox">{{
                    option_name }}</label>
                </div>
              </template>
            </td>
          </tr>
        </template>

        <template v-for="(part_data, part_name) in component['parts']" :key="part_name">
          <template v-if="is_selected_module(part_name)">
            <tr>
              <td class="space"></td>
            </tr>
            <tr class="part-name">
              <td>{{ part_name }}</td>
              <td colspan="2"></td>
              <td>{{ getPC(part_data.weight) }}</td>
              <td>{{ getPC(part_data.weight * component.weight) }}</td>
            </tr>
            <template v-for="(coursework_data, coursework_name) in part_data['courseworks']" :key="coursework_name">
              <tr class="coursework">
                <td>{{ coursework_name }}</td>
                <template v-if="coursework_data.is_percent">
                  <td colspan="2">
                    <va-input class="mark-input" label="Percentage mark"
                      v-model="user_data[component['name']][part_name][coursework_name]" />
                  </td>
                </template>
                <template v-else-if="coursework_data.is_pass_fail">
                  <td colspan="2">
                    <div class="checkbox">
                      <input type="checkbox" v-model="user_data[component['name']][part_name][coursework_name]" />
                    </div>
                  </td>
                </template>
                <template v-else>
                  <td>
                    <va-input class="mark-input" v-model="user_data[component['name']][part_name][coursework_name]" />
                  </td>
                  <td>{{ coursework_data.marks }}</td>
                </template>
                <td>{{ getPC(coursework_data.weight * part_data.weight * part_data.coursework_weight) }}</td>
                <td>{{ getPC(coursework_data.weight * part_data.weight * component.weight * part_data.coursework_weight)
                  }}
                </td>
              </tr>
            </template>
            <template v-for="(exam_data, exam_name) in part_data['exams']" :key="exam_name">
              <tr class="exam">
                <td>{{ exam_name }}</td>
                <template v-if="exam_data.is_percent">
                  <td colspan="2">
                    <va-input class="mark-input" label="Percentage mark"
                      v-model="user_data[component['name']][part_name][exam_name]" />
                  </td>
                </template>
                <template v-else>
                  <td>
                    <va-input class="mark-input" v-model="user_data[component['name']][part_name][exam_name]" />
                  </td>
                  <td>{{ exam_data.marks }}</td>
                </template>
                <td>{{ getPC(exam_data.weight * part_data.weight * (1 - (part_data.coursework_weight || 0))) }}</td>
                <td>{{ getPC(exam_data.weight * part_data.weight * component.weight * (1 - (part_data.coursework_weight || 0)))
                  }}
                </td>
              </tr>
            </template>
            <tr class="part-grade">
              <td></td>
              <td>Percentage:</td>
              <td colspan="3">{{ format_part_percentage_output(component['name'], part_name) }}</td>
            </tr>
            <tr class="part-grade">
              <td></td>
              <td>Grade:</td>
              <td colspan="3">{{ format_part_grade_output(component['name'], part_name) }}</td>
            </tr>
          </template>
        </template>
        <tr>
          <td class="space"></td>
        </tr>
        <tr class="component-grade">
          <td><b>{{ component.name }}</b> Percentage:</td>
          <td colspan="3">{{ format_component_percentage_output(component['name']) }}</td>
        </tr>
        <tr class="component-grade">
          <td><b>{{ component.name }}</b> Grade:</td>
          <td colspan="3">{{ format_component_grade_output(component['name']) }}</td>
        </tr>
      </tbody>
      <tr>
        <td class="space"></td>
      </tr>
      <tr>
        <td class="space"></td>
      </tr>
      <tr class="overall-grade">
        <td><b>Overall</b> Percentage:</td>
        <td colspan="2">{{ format_overall_percentage_output() }}</td>
      </tr>
      <tr class="overall-grade">
        <td><b>Overall</b> Grade:</td>
        <td colspan="2">{{ format_overall_grade_output() }}</td>
      </tr>
      <tr class="overall-grade">
        <td>Pass all:</td>
        <td colspan="2">{{ format_examinable_pass_output() }}</td>
      </tr>
      <template v-if="'Practical Component' in user_data">
        <tr class="overall-grade">
          <td>Pass laboratory:</td>
          <td colspan="2">{{ format_lab_pass_output() }}</td>
        </tr>
      </template>
      <tr class="overall-grade">
        <td>Pass year:</td>
        <td colspan="2">{{ format_pass_output() }}</td>
      </tr>
      <template v-if="this.progress_to_meng">
        <tr class="overall-grade">
          <td>Progress to MEng:</td>
          <td colspan="2">{{ format_progress_MEng_output() }}</td>
        </tr>
      </template>
      <tr>
        <td class="space"></td>
      </tr>
      <tr>
        <td class="space"></td>
      </tr>
    </table>
  </div>
</template>
