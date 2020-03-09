import { Component, OnInit } from '@angular/core';
import { BackendService } from '../backend.service';
@Component({
  selector: 'app-start-page',
  templateUrl: './start-page.component.html',
  styleUrls: ['./start-page.component.css']
})
export class StartPageComponent implements OnInit {

  constructor(private backend: BackendService) { }

  ngOnInit(): void {
  }

  spin() {
    this.backend.spinMotor().subscribe(console.log);
  }

}
