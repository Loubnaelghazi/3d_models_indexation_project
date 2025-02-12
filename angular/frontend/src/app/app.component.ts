import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { Router } from '@angular/router';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
})
export class AppComponent {
  title = 'frontend';
  activeItem: string = 'dashboard';
  constructor(private router: Router) {}
  
  goTo(path: string): void {
    this.router.navigate([path]);
  }
}
