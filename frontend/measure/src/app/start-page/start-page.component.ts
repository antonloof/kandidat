import { Component, OnInit, ViewChild } from '@angular/core';
import { BackendService } from '../backend.service';
import { PaginatedList } from '../classes/paginated-list';
import { Measurement, CreateMeasurement } from '../classes/measurement';
import { PageEvent } from '@angular/material/paginator';
import { MatTable } from '@angular/material/table';
import { MatDialog, MatDialogConfig } from '@angular/material/dialog';

import { MeasureDialogComponent } from '../measure-dialog/measure-dialog.component';

@Component({
  selector: 'app-start-page',
  templateUrl: './start-page.component.html',
  styleUrls: ['./start-page.component.css'],
})
export class StartPageComponent implements OnInit {
  constructor(private backend: BackendService, private dialog: MatDialog) {}

  @ViewChild(MatTable) table: MatTable<Measurement>;

  measurements: PaginatedList<Measurement>;
  columns_to_display: string[] = [
    'id',
    'name',
    'description',
    'created_at',
    'mobility',
    'sheet_resistance',
    'state',
    'action',
  ];
  filters: any = {};
  page_size_options = [10, 25, 50];

  ngOnInit(): void {
    this.fetch_page();
  }

  openDialog() {
    const dialogConfig = new MatDialogConfig();
    dialogConfig.disableClose = false;
    dialogConfig.autoFocus = true;
    this.dialog.open(MeasureDialogComponent, dialogConfig);
  }

  reset_filters(): void {
    this.filters = {};
    this.fetch_page();
  }

  fetch_page(page?: PageEvent): void {
    let query_params = {
      ...this.format_filters(),
      limit: this.page_size_options[0],
    };
    if (page) {
      query_params = {
        ...query_params,
        limit: page.pageSize,
        offset: page.pageSize * page.pageIndex,
      };
    }
    this.backend.get_measurements(query_params).subscribe(res => {
      this.measurements = res;
    });
  }

  close_measurement(id: number): void {
    this.backend.update_measurement(id, { open: false }).subscribe(res => {
      const i = this.measurements.results.findIndex(
        measurement => measurement.id === id
      );
      this.measurements.results[i] = res;
      this.table.renderRows();
    });
  }

  private format_filters(): any {
    const formatted_filters = {};
    Object.entries(this.filters).forEach(kvp => {
      const k = kvp[0];
      const v = kvp[1];
      if (v instanceof Date) {
        formatted_filters[k] = v.toISOString();
      } else {
        formatted_filters[k] = v;
      }
    });
    return formatted_filters;
  }
}
