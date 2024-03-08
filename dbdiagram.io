// Use DBML to define your database structure
// Docs: https://dbml.dbdiagram.io/docs

Table classes {
  id integer [primary key]
  name text
  title text
  credits text
  description text
  prerequisites text
  recommended text
  warnings text
  substitutions text
  pre text
  pre_credits text
  pre_notes text
  catalog_id integer [ref: > catalog.id]
}

Table degrees {
  id integer [primary key]
  name text
  type text
}

Table programs {
  id integer [primary key]
  name text
  degree_id integer [ref: > degrees.id]
  catalog_id integer [ref: > catalog.id]
}

Table course_type {
  id integer [primary key]
  name text
  label text
}

Table program_sequence {
  seq integer
  program_id integer [ref: > programs.id]
  name text
  class_id integer [ref: > classes.id]
  course_type_id integer [ref: > course_type.id]
}

Table roles {
  id integer [primary key]
  type text
}

Table resident_status {
  id integer [primary key]
  type text
}

Table catalog {
  id integer [primary key]
  name text
}

Table users {
  id integer [primary key]
  role_id integer [ref: > roles.id]
  username text
  firstname text
  lastname text
  created_at timestamp
}

Table student_info {
  id integer [primary key]
  user_id integer [ref: > users.id]
  resident_status_id integer [ref: > resident_status.id]
  program_id integer [ref: > programs.id]
  notes text
}

Table menu_areas {
  id integer [primary key]
  name text
}

Table menu_degrees {
  id integer [primary key]
  name text
}

Table menu_programs_by_areas {
  id integer [primary key]
  menu_area_id integer [ref: > menu_areas.id]
  menu_degree_id integer [ref: > menu_degrees.id]
  program_id integer  [ref: > programs.id]
}

Table student_progress {
  id integer [primary key]
  student_info_id integer [ref: > student_info.id]
  seq integer
  name text
  credits integer
  type text
  completed integer
  period integer
  session integer
  prerequisite text
}