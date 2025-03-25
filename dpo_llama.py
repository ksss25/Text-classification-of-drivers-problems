from datasets import load_dataset
from trl import DPOConfig, DPOTrainer
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model
import torch
import os

os.environ['PYTORCH_MPS_HIGH_WATERMARK_RATIO'] = '0.0'
os.environ['PYTORCH_MPS_MAX_CACHE_SIZE'] = '1'
path = "./Llama-3.1-8B"

tokenizer = AutoTokenizer.from_pretrained(path, padding_side='right')
tokenizer.pad_token = tokenizer.eos_token or '<pad>'

print('LOADING MODEL...')
model = AutoModelForCausalLM.from_pretrained(
    path,
    device_map="auto",
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
)

lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)
model = get_peft_model(model, lora_config)
model.config.use_cache = False

print('MODEL WAS SUCCESSFULLY LOADED WITH LORA!')

print('LOADING DATASET...')
train_dataset = load_dataset('csv', data_files='s')['train']
print('DATASET IS READY')

training_args = DPOConfig(
    per_device_train_batch_size=1,
    gradient_accumulation_steps=8,
    output_dir="llama_dpo_results",
    learning_rate=5e-6,
    optim="adamw_torch",
    max_grad_norm=0.3,
    beta=0.1,
    max_length=512,
    max_prompt_length=512,
    remove_unused_columns=False,
    dataloader_pin_memory=False
)

print('INITIALIZING TRAINER')
sample_input = tokenizer("Test input", return_tensors="pt").to(model.device)
output = model(**sample_input)

trainer = DPOTrainer(
    model=model,
    ref_model=None,
    args=training_args,
    processing_class=tokenizer,
    train_dataset=train_dataset
)

print('STARTING TRAINING...')
try:
    trainer.train()
    model.save_pretrained("llama3.1-8b-dpo-trained")
    tokenizer.save_pretrained("llama3.1-8b-dpo-trained")
    print('SUCCESS!')
except Exception as e:
    print(f'Training failed: {str(e)}')