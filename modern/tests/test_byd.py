# SPDX-License-Identifier: GPL-2.0-only
from pathlib import Path
import re,subprocess,sys,os,shlex,tempfile
source=Path(sys.argv[1] if len(sys.argv)>1 else Path(__file__).resolve().parents[1]/'byd.c').read_text()
def function(name):
 start=source.index(name+'(');start=source.rfind('\n',0,start)+1
 brace=source.index('{',start);depth=1;i=brace+1
 while depth:
  depth+=(source[i]=='{')-(source[i]=='}');i+=1
 return source[start:i]
defs='\n'.join(x for x in source.splitlines() if x.startswith('#define BYD_') or x.startswith('#define PS2_'))
pre='''#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
typedef uint8_t u8; typedef uint16_t u16; typedef int psmouse_ret_t;
#define BIT_MASK(x) (1UL << (x))
#define ARRAY_SIZE(x) (sizeof(x)/sizeof((x)[0]))
#define PSMOUSE_BAD_DATA -1
#define PSMOUSE_FULL_PACKET 1
#define PSMOUSE_ACTIVATED 1
#define PSMOUSE_CMD_SETRATE 0x10f3
#define PSMOUSE_CMD_GETID 0x02f2
#define PSMOUSE_CMD_ENABLE 0x00f4
#define PSMOUSE_CMD_DISABLE 0x00f5
#define REL_X 0
#define REL_Y 1
#define REL_HWHEEL 6
#define REL_WHEEL 8
#define BTN_LEFT 272
#define BTN_RIGHT 273
struct input_dev { int unused; };
struct ps2dev { int unused; };
struct byd_data { bool btn_left, btn_right; int timer; };
struct psmouse { struct input_dev *dev; void *private; u8 packet[4]; struct ps2dev ps2dev; };
struct event { int kind, code, value; }; static struct event events[32]; static int count;
static void input_report_rel(struct input_dev *d,int c,int v) { (void)d;events[count++]=(struct event){0,c,v}; }
static void input_report_key(struct input_dev *d,int c,int v) { (void)d;events[count++]=(struct event){1,c,!!v}; }
static void input_sync(struct input_dev *d) { (void)d;events[count++]=(struct event){2,0,0}; }
static void timer_delete(int *t) { (void)t; }
static void kfree(void *p) { (void)p; }
static void psmouse_warn(struct psmouse *p,const char *s) { (void)p;(void)s; }
static bool byd_firmware_scroll;
static bool magic_ok=true; static int fail_command, resets; static u8 args[256];
static int ps2_command(struct ps2dev *d,u8 *p,u16 c) {
 (void)d;
 if (c==fail_command) { fail_command=0; return -1; }
 if(p) args[c&255]=p[0];
 if(c==0x14e0) {p[0]=magic_ok?8:0;p[1]=1;p[2]=1;p[3]=0x31;}return 0;
}
static int psmouse_reset(struct psmouse *p) {(void)p;resets++;return 0;}
static void psmouse_set_state(struct psmouse *p,int state) {(void)p;(void)state;}
'''
tests='''
static void packet(struct psmouse *p,int flags,int x,int y,int code) {
 count=0;p->packet[0]=flags;p->packet[1]=x;p->packet[2]=y;p->packet[3]=code;
}
static void expect(int n,int kind,int code,int value) {
 assert(n<count);assert(events[n].kind==kind);assert(events[n].code==code);assert(events[n].value==value);
}
int main(void) {
 struct input_dev dev={0};struct byd_data data={0};struct psmouse p={.dev=&dev,.private=&data};
 int codes[]={0xd5,0x2b,0x2a,0xd6};int axes[]={8,8,6,6};int values[]={1,-1,1,-1};
 for(int i=0;i<4;i++) {packet(&p,8,0,0,codes[i]);assert(byd_process_firmware_packet(&p)==1);assert(count==2);expect(0,0,axes[i],values[i]);expect(1,2,0,0);}
 packet(&p,0x39,255,254,0);assert(byd_process_firmware_packet(&p)==1);
 expect(0,0,REL_X,-1);expect(1,0,REL_Y,2);expect(2,1,BTN_LEFT,1);expect(3,1,BTN_RIGHT,0);
 packet(&p,8,0,0,0);assert(byd_process_firmware_packet(&p)==1);expect(2,1,BTN_LEFT,0);
 packet(&p,8,0,0,0xf8);assert(byd_process_firmware_packet(&p)==1);assert(count==0);
 packet(&p,8,0,0,0x55);assert(byd_process_firmware_packet(&p)==-1);assert(count==0);
 byd_firmware_scroll=false;magic_ok=false;assert(byd_reset_touchpad(&p)==0);
 assert(args[0xe3]==2 && args[0xd2]==4 && args[0xe5]==4);
 byd_firmware_scroll=true;magic_ok=true;assert(byd_reset_touchpad(&p)==0);
 assert(args[0xe3]==1 && args[0xd2]==3 && args[0xe5]==0);
 // A failed signature must reset hardware out of vendor command mode.
 magic_ok=false;resets=0;assert(byd_reset_touchpad(&p)==-ENODEV);assert(resets==1);
 magic_ok=true;fail_command=0x10d2;resets=0;assert(byd_reset_touchpad(&p)==-EIO);assert(resets==1);assert(args[0xd1]==0);assert(args[0xe3]==2);assert(args[0xd2]==4);fail_command=0;
 // Corner gestures must create separate press/release frames, not resync.
 packet(&p,8,0,0,0x2e);assert(byd_process_firmware_packet(&p)==1);assert(count==4);
 expect(0,1,BTN_LEFT,1);expect(1,2,0,0);expect(2,1,BTN_LEFT,0);expect(3,2,0,0);
 packet(&p,8,0,0,0xd2);assert(byd_process_firmware_packet(&p)==1);assert(count==4);
 expect(0,1,BTN_RIGHT,1);expect(2,1,BTN_RIGHT,0);
 // Unbinding a configured pad must disable firmware packets BEFORE free.
 args[0xd1]=2;args[0xe3]=1;args[0xd2]=3;args[0xe5]=0;
 byd_disconnect(&p);
 assert(args[0xd1]==0);assert(args[0xe3]==2);assert(args[0xd2]==4);assert(args[0xe5]==4);
 assert(p.private==NULL);assert(args[0xd4]==1);
 // A failed disable setting must still leave vendor command mode and reset.
 fail_command=0x10d1;resets=0;args[0xe2]=0;
 assert(byd_restore_relative(&p)==-EIO);assert(args[0xe2]==1);assert(resets==1);fail_command=0;
 // Failed stream disable still attempts firmware cleanup.
 fail_command=PSMOUSE_CMD_DISABLE;args[0xd1]=2;resets=0;
 assert(byd_restore_relative(&p)==-EIO);assert(args[0xd1]==0);assert(resets==1);
 // Failed gesture cleanup must not skip absolute-mode cleanup.
 fail_command=BYD_CMD_SET_MULTITOUCH;args[0xd1]=2;resets=0;
 assert(byd_restore_relative(&p)==-EIO);assert(args[0xd1]==0);assert(resets==1);
 // Ordinary BYD profile teardown must retain upstream behavior.
 p.private=&data;byd_firmware_scroll=false;resets=0;args[0xd1]=2;
 byd_disconnect(&p);assert(resets==0);assert(args[0xd1]==2);assert(p.private==NULL);
 puts("PASS: wheel directions, signed motion, physical buttons, ignored absolute packets, unknown packets, default profile, firmware profile, signature rejection, reset on failure, corner click frames, relative-mode teardown, failure cleanup, unchanged default teardown.");
}
'''
tmp=tempfile.TemporaryDirectory();p=Path(tmp.name);c=p/'probe.c';c.write_text(pre+'\n'+defs+'\n'+function('byd_process_firmware_packet')+'\n'+function('byd_restore_relative')+'\n'+function('byd_reset_touchpad')+'\n'+function('byd_disconnect')+'\n'+tests)
subprocess.run(shlex.split(os.environ.get('CC','cc'))+['-std=gnu11','-Wall','-Wextra','-Werror','-Wno-unused-function','-fsanitize=undefined',str(c),'-o',str(p/'probe')],check=True)
r=subprocess.run([str(p/'probe')]);sys.exit(r.returncode)
