import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'sheetResistance',
})
export class SheetResistancePipe implements PipeTransform {
  transform(value: number): string {
    if (!value && value !== 0) {
      return '';
    }
    const resolution = 1e4;
    return `${parseFloat(value.toPrecision(4))} Ω`;
  }
}
