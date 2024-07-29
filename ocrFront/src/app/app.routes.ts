import { Routes } from '@angular/router';
import {TunisianCinComponent} from "./tunisian-cin/tunisian-cin.component";
import {TunisianPassportComponent} from "./tunisian-passport/tunisian-passport.component";
import {EgyptianCinComponent} from "./egyptian-cin/egyptian-cin.component";
import {EditorComponent} from "./editor/editor.component";
import {CategoryComponent} from "./category/category.component";
import {ScannerComponent} from "./scanner/scanner.component";

export const routes: Routes = [{path:'',component:TunisianCinComponent},
  {path:'tunPassport',component:TunisianPassportComponent},
  {path:'editor',component:EditorComponent},
  {path:'egyptCin',component:EgyptianCinComponent},
  {path:'scanner',component:ScannerComponent},
  {path:'category',component:CategoryComponent}];
