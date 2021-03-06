import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { HttpClientModule } from '@angular/common/http';
import { RouterModule, Routes } from '@angular/router';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { TitleCasePipe } from '@angular/common';

import { MatInputModule } from '@angular/material/input';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatTableModule } from '@angular/material/table';
import { MatGridListModule } from '@angular/material/grid-list';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatDialogModule } from '@angular/material/dialog';
import { MatSelectModule } from '@angular/material/select';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';

import { AppComponent } from './app.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { StartPageComponent } from './start-page/start-page.component';
import { MobilityPipe } from './pipe/mobility.pipe';
import { SheetResistancePipe } from './pipe/sheet-resistance.pipe';
import { AboutComponent } from './about/about.component';
import { MeasureDialogComponent } from './measure-dialog/measure-dialog.component';
import { DetailsComponent } from './details/details.component';
import { SpeedPipe } from './pipe/speed.pipe';
import { ChartsModule } from 'ng2-charts';
import { FlexLayoutModule } from '@angular/flex-layout';
import { CloseDialogComponent } from './close-dialog/close-dialog.component';
import { ToprecisionPipe } from './pipe/toprecision.pipe';

const routes: Routes = [
  { path: '', component: StartPageComponent },
  { path: 'about', component: AboutComponent },
  { path: 'details/:id', component: DetailsComponent },
];

@NgModule({
  declarations: [
    AppComponent,
    StartPageComponent,
    MobilityPipe,
    SheetResistancePipe,
    AboutComponent,
    MeasureDialogComponent,
    DetailsComponent,
    SpeedPipe,
    CloseDialogComponent,
    ToprecisionPipe,
  ],
  imports: [
    FormsModule,
    RouterModule.forRoot(routes),
    BrowserModule,
    BrowserAnimationsModule,
    HttpClientModule,
    MatInputModule,
    MatCardModule,
    MatButtonModule,
    MatPaginatorModule,
    MatTableModule,
    MatGridListModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatDialogModule,
    MatSelectModule,
    MatIconModule,
    MatTooltipModule,
    ReactiveFormsModule,
    ChartsModule,
    FlexLayoutModule,
  ],
  providers: [SpeedPipe, MobilityPipe, SheetResistancePipe, TitleCasePipe],
  bootstrap: [AppComponent],
  entryComponents: [MeasureDialogComponent, CloseDialogComponent],
})
export class AppModule {}
