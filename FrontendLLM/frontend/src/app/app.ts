import { Component } from '@angular/core';
import { SmartChatComponent } from './components/smart-chat/smart-chat';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [SmartChatComponent],
  template: `<app-smart-chat />`,
})
export class App {}
