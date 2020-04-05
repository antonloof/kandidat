import { Component, OnInit } from '@angular/core';
import { BackendService } from '../backend.service';
@Component({
  selector: 'app-start-page',
  templateUrl: './start-page.component.html',
  styleUrls: ['./start-page.component.css'],
})
export class StartPageComponent implements OnInit {
  constructor(private backend: BackendService) {}

  ngOnInit(): void {}

  measure() {
    this.backend
      .measure({
        connection_1: 1,
        connection_2: 3,
        connection_3: 5,
        connection_4: 2,
        current_limit: 10e-6,
      })
      .subscribe(res => {
        console.log(res);
      });
  }
}
