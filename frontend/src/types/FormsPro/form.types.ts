import { FormField } from "./form_field.types";

export interface Form {
  name: string;
  creation: string;
  modified: string;
  owner: string;
  modified_by: string;
  docstatus: 0 | 1 | 2;
  parent?: string;
  parentfield?: string;
  parenttype?: string;
  idx?: number;
  /**	Is Published? : Check	*/
  is_published?: 0 | 1;
  /**	Route : Data	*/
  route?: string;
  /**	Title : Data	*/
  title: string;
  /**	Linked Doctype : Link - DocType	*/
  linked_doctype: string;
  /**	Linked Team : Link - FP Team	*/
  linked_team_id: string;
  /**	Login Required : Check	*/
  login_required?: 0 | 1;
  /**	Allow Incomplete Forms : Check - Allow saving Draft forms	*/
  allow_incomplete?: 0 | 1;
  /**	Success Title : Data	*/
  success_title?: string;
  /**	Success Description : Text Editor	*/
  success_description?: string;
  /**	Description : Text Editor	*/
  description?: string;
  /**	Fields : Table - Form Field	*/
  fields?: FormField[];
  /**	Meta Data : Code	*/
  metadata?: string;
}
