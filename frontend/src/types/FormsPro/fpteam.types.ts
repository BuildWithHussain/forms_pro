import { FPTeamMember } from "./fpteam_member.types";

export interface FPTeam {
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
  /**	Logo : Attach Image	*/
  logo?: string;
  /**	Team Name : Data	*/
  team_name: string;
  /**	Users : Table MultiSelect - FP Team Member	*/
  users?: FPTeamMember[];
}
