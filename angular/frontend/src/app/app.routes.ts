import { Routes } from '@angular/router';
import { IndexationComponent } from './indexation/indexation.component';
import { HomeComponent } from './home/home.component';

export const routes: Routes = [
  { path: '', component: HomeComponent }, // Page d'accueil
  { path: 'indexation', component: IndexationComponent }
];

