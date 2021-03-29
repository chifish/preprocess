import re
from tqdm import tqdm
from langdetect import detect
import editdistance

s1 = []
s2 = []
file_in = 'para-nmt-50m.txt'
num_lines = 51409584

with open(file_in, 'r', encoding='utf8') as f_in, open('para_out.txt', 'w', encoding='utf8') as f_out:
	for _, line_raw in enumerate(tqdm(f_in, desc="Lines", total=num_lines)):
		line = line_raw.strip().split('\t')
		src = line[0]
		trg = line[1]
		pair = '\t'.join(line[:2])
		score = float(line[2])
		if score < 0.6 or score > 0.8:
			continue
		len1 = len(src.split())
		len2 = len(trg.split())
		if len1 < 5 or len2 < 5:
			continue
		if len1 > 50 or len2 > 50:
			continue
		if re.search(r"^[\da-zA-Z\'\"]", src) is None or re.search(r"^[\da-zA-Z\'\"]", trg) is None:
			continue
		if len(re.findall(r"[#▐+|€/♪…*±=—º\(\)»«‘’“”`´●¨]", pair)) > 0:#•
			print("BAD_SYMBOL\t" + src +'\t'+ trg)
			continue
		if len(re.findall(r"\(", pair)) > 0:
			print("BAD_SYMBOL(\t" + src +'\t'+ trg)
			continue
		if len(re.findall(r"\)", pair)) > 0:
			print("BAD_SYMBOL)\t" + src +'\t'+ trg)
			continue
		if len(re.findall(r"\[", pair)) > 0:
			print("BAD_SYMBOL[\t" + src +'\t'+ trg)
			continue
		if len(re.findall(r"]", pair)) > 0:
			print("BAD_SYMBOL]\t" + src +'\t'+ trg)
			continue
		if len(re.findall(r"\.\.\.\s*\.\.\.", pair)) > 0:
			print("BAD_SYMBOL_*\t" + src +'\t'+ trg)
			continue
		if len(re.findall(r"[a-zA-Z]+\?[a-zA-Z]+", pair)) > 0:
			print("QUESTION_MARK\t" + src +'\t'+ trg)
			continue
		if len(re.findall(r"\d\.\d", pair)) > 0:
			print("DECIMAL\t" + src +'\t'+ trg)
			continue
		if len(re.findall(r"\'il\s", pair)) > 0:
			print("IL\t" + src +'\t'+ trg)
			continue
		if len(re.findall(r"^\d", src)) > 0:
			tmp = src.split()[1]
			if not tmp.isalpha() or tmp[0].isupper(): #34 –
				print("LEADING_NUM\t" + src +'\t'+ trg)
				continue
		if re.search(r"^\d", trg) is not None:
			tmp = trg.split()[1]
			if not tmp.isalpha() or tmp[0].isupper():
				print("LEADING_NUM\t" + src +'\t'+ trg)
				continue

		if len(re.findall(r"\d+\s+\d+", pair)) > 0:
			print("DOUBEL_NUM\t" + src +'\t'+ trg)
			continue
		if len(re.findall(r"\d+", src)) > 2 or len(re.findall(r"\d+", trg)) > 2:
			print("MANY_NUM\t" + src +'\t'+ trg)
			continue
		if len(re.findall(r"\"", src)) % 2 != 0 or len(re.findall(r"\"", trg)) % 2 != 0:
			print("QUOTES_UNMATCH\t" + src +'\t'+ trg)
			continue
		n1 = len(re.findall(r"[,\.\?]", src))
		n2 = len(re.findall(r"[,\.\?]", trg))
		if n1 * 1.0 / len1 > 0.2:
			if len(re.findall(r"\.", src)) == 3:
				if len(re.findall(r"\.\.\.", src)) != 1:
					print("MANY_PUNK_1\t" + src +'\t'+ trg)
					continue
			else:
				print("MANY_PUNK\t" + src +'\t'+ trg)
				continue
		if n2 * 1.0 / len2 > 0.2:
			if len(re.findall(r"\.", trg)) == 3:
				if len(re.findall(r"\.\.\.", trg)) != 1:
					print("MANY_PUNK_2\t" + src +'\t'+ trg)
					continue
			else:
				print("MANY_PUNK\t" + src +'\t'+ trg)
				continue
		if max(len1, len2) * 1.0 / min(len1, len2) > 1.5:
			print("LEN_UNMATCH\t" + src +'\t'+ trg)
			continue
		try:
			lang1 = detect(src)
		except Exception as e:
			print(f"Exception: {e.get_code()}")
			print(src +'\t'+ trg)
			continue
		try:
			lang2 = detect(trg)
		except Exception as e:
			print(f"Exception: {e.get_code()}")
			print(src +'\t'+ trg)
			continue
		if lang1 != 'en' or lang2 != 'en':
			print("NOT ENGLISH:\t" + src +'\t'+ trg)
			continue
		zh_tmp = re.sub(r"[\s,\.]", "", src)
		en_tmp = re.sub(r"[\s,\.]", "", trg)
		min_len = min(len(zh_tmp), len(en_tmp))
		dist = editdistance.eval(zh_tmp.lower(), en_tmp.lower())
		ratio = dist * 1.0 / min_len
		if ratio < 0.4:
			print(f"OVERLAP {ratio}:\t" + src +'\t'+ trg)
			continue
		if len(src) > len(trg):
			long_txt = src
			shrt_txt = trg
			len_short = len(trg)
		else:
			long_txt = trg
			shrt_txt = src
			len_short = len(src)
		segment1 = long_txt[:len_short]
		segment2 = long_txt[-len_short:]
		dist1 = editdistance.eval(segment1.lower(), shrt_txt.lower())
		ratio1 = dist1 * 1.0 / len_short
		if ratio1 < 0.2:
		    print(f"SEGMENT {ratio1}:\t" + src +'\t'+ trg)
			continue
		dist2 = editdistance.eval(segment2.lower(), shrt_txt.lower())
		ratio2 = dist2 * 1.0 / len_short
		if ratio2 < 0.2:
			print(f"SEGMENT {ratio2}:\t" + src +'\t'+ trg)
			continue
		if re.search(r"in'[a-rt-z\s]", src, flags=re.IGNORECASE) is not None or re.search(r"in'[a-rt-z\s]", trg, flags=re.IGNORECASE) is not None:
			print("IN'\t" + src +'\t'+ trg)
			continue
		if re.search(r"([a-zA-Z]+)-?\1-?\1", src, flags=re.IGNORECASE) is not None or re.search(r"([a-zA-Z]+)-?\1-?\1", trg, flags=re.IGNORECASE) is not None:
			print("REPEAT\t" + src +'\t'+ trg)
			continue
		if re.search(r"\w+[A-Z]+[a-zA-Z]+\s", src) is not None or re.search(r"\w+[A-Z]+[a-zA-Z]+\s", trg):
			print("UPPER\t" + src +'\t'+ trg)
			continue
		if re.search(r"[A-Z]+[a-z]+[A-Z]+", src) is not None or re.search(r"[A-Z]+[a-z]+[A-Z]+", trg):
			print("AaA\t" + src +'\t'+ trg)
			continue
		if re.search(r"\s[,:;\.][a-zA-Z]", line) is not None:
			print("DOT\t" + src +'\t'+ trg)
			continue
		if len(re.findall(r"'", src)) == 1:
			if re.search(r"\s'", src) is not None or re.search(r"'$", src):
				print("SINGLE_QUOTE\t" + src +'\t'+ trg)
				continue
		if len(re.findall(r"'", trg)) == 1:
			if re.search(r"\s'", trg) is not None or re.search(r"'$", trg):
				print("SINGLE_QUOTE\t" + src +'\t'+ trg)
				continue		
		if re.search(r"[a-zA-Z\s]+[,\.!?-][\"\']", src) is not None or re.search(r"[a-zA-Z\s]+[,\.!?-][\"\']", trg):
			print("PUNK_B4_Q\t" + src +'\t'+ trg)
			continue
		if re.search(r"[-:]$", src) is not None or re.search(r"[-:]$", trg):
			print("END_HYPHEN_COLON\t" + src +'\t'+ trg)
			continue
		if re.search(r"\d[a-ru-z]{2,}", line) is not None:
			print("DOT\t" + src +'\t'+ trg)
			continue
		ds =  re.findall(r"\d+s[a-z,\.]*[\s\n]", src)
		if len(ds) > 0:
			flag = False
			for s in ds:
				if not re.match(r"\d+st[\s\n]", s) and not re.match(r"\d+s[\s\n]", s):
					flag = True
					break
			if flag:
				print("num_src\t" + src +'\t'+ trg)
				continue
		ds =  re.findall(r"\d+s[a-z,\.]*[\s\n]", trg)
		if len(ds) > 0:
			flag = False
			for s in ds:
				if not re.match(r"\d+st[\s\n]", s) and not re.match(r"\d+s[\s\n]", s):
					flag = True
					break
			if flag:
				print("num_trg\t" + src +'\t'+ trg)
				continue
		if re.search(r"[a-z]\d", src) is not None or re.search(r"[a-z]\d", trg):
			print("letter_num\t" + src +'\t'+ trg)
			continue
		if re.search(r"[a-z]+-[a-z]+-[a-z]+-", src, flags=re.IGNORECASE) is not None or re.search(r"[a-z]+-[a-z]+-[a-z]+-", trg, flags=re.IGNORECASE):
			print("hyphen_hyphen\t" + src +'\t'+ trg)
			continue
		if re.search(r"\s[b-hj-z][,;:\s]", src, flags=re.IGNORECASE) or re.search(r"\s[b-hj-z][,;:\s]", trg, flags=re.IGNORECASE):
			print("SINGLE_LETTER\t" + src +'\t'+ trg)
			continue
		if re.search(r"%", src) is not None and re.search(r"\d\s?%", src) is None:
			print("Percentage_src\t" + src +'\t'+ trg)
			continue
		if re.search(r"%", trg) is not None and re.search(r"\d\s?%", trg) is None:
			print("Percentage_trg\t" + src +'\t'+ trg)
			continue
		if re.search(r"^\w+:", src) is not None or re.search(r"^\w+:", trg):
			print("COLON\t" + src +'\t'+ trg)
			continue
		if re.search(r"^[a-zA-Z]+\s\d+\s[A-Z]", src) is not None or re.search(r"^[a-zA-Z]+\s\d+\s[A-Z]", trg):
			print("NUMBERING_START\t" + src +'\t'+ trg)
			continue
		if re.search(r"\'il\s", src, flags=re.IGNORECASE) is not None or re.search(r"\'il\s", trg, flags=re.IGNORECASE):
			print("IL\t" + src +'\t'+ trg)
			continue
		if re.search(r"\s[a-z]-[a-z]+", src, flags=re.IGNORECASE) is not None or re.search(r"\s[a-z]-[a-z]+", trg, flags=re.IGNORECASE):
			print("HYPHEN\t" + src +'\t'+ trg)
			continue
		if re.search(r"[a-z]'[a-ce-ln-ru-z]\s", src, flags=re.IGNORECASE) is not None or re.search(r"[a-z]'[a-ce-ln-ru-z]\s", trg, flags=re.IGNORECASE):
			print("SINGLE_QUO_1\t" + src +'\t'+ trg)
			continue
		if re.search(r"[a-z]'[a-z]{2}\s", src, flags=re.IGNORECASE) is not None and re.search(r"[a-z]'[rvl][el]\s", src, flags=re.IGNORECASE) is None:
			print("SINGLE_QUO_2\t" + src +'\t'+ trg)
			continue
		if re.search(r"[a-z]'[a-z]{2}\s", trg, flags=re.IGNORECASE) is not None and re.search(r"[a-z]'[rvl][el]\s", trg, flags=re.IGNORECASE) is None:
			print("SINGLE_QUO_2\t" + src +'\t'+ trg)
			continue
		if re.search(r"[a-z]'[a-z]{3,}\s", src, flags=re.IGNORECASE) is not None or re.search(r"[a-z]'[a-z]{3,}\s", trg, flags=re.IGNORECASE):
			print("SINGLE_QUO_3\t" + src +'\t'+ trg)
			continue
		if re.search(r"¿_•\\", line) is not None:
			print("BAD_CHAR\t" + src +'\t'+ trg)
			continue
		if re.search(r"-\s?-\s?-", line) is not None:
			print("hyphens---\t" + src +'\t'+ trg)
			continue
		toks_1 = [t.text for t in nlp(src)]
		src_tok = ' '.join(toks_1)
		len1 = len(toks_1)
		cap = len(re.findall(r"\s[A-Z]\w+", src_tok))
		if cap * 1.0 / len1 > 0.2:
			print("cap_words\t" + src +'\t'+ trg)
			continue
		toks_2 = [t.text for t in nlp(trg)]
		trg_tok = ' '.join(toks_2)
		len2 = len(toks_2)
		if len1 > 30 or len2 > 30 or len1 < 5 or len2 < 5:
			continue
		if max(len1, len2) * 1.0 / min(len1, len2) > 1.5:
			print("LEN_UNMATCH\t" + src +'\t'+ trg)
			continue
		cap = len(re.findall(r"\s[A-Z]\w+", trg_tok))
		if cap * 1.0 / len2 > 0.2:
			print("cap_words\t" + src +'\t'+ trg)
			continue
		word_len1 = [len(w) for w in toks_1]
		if max(word_len1) > 20:
			print(f"word_too_long {max(word_len1)}\t" + src +'\t'+ trg)
			continue
		word_len2 = [len(w) for w in toks_2]
		if max(word_len2) > 20:
			print(f"word_too_long {max(word_len2)}\t" + src +'\t'+ trg)
			continue
		n1 = len(re.findall(r"[,\.\?-]", src))#add hyphen
		n2 = len(re.findall(r"[,\.\?-]", trg))
		if n1 * 1.0 / len1 > 0.2:
			if len(re.findall(r"\.", src)) == 3:
				if len(re.findall(r"\.\.\.", src)) != 1:
					print("MANY_PUNK_1\t" + src +'\t'+ trg)
					continue
			else:
				print("MANY_PUNK_1\t" + src +'\t'+ trg)
				continue
		if n2 * 1.0 / len2 > 0.2:
			if len(re.findall(r"\.", trg)) == 3:
				if len(re.findall(r"\.\.\.", trg)) != 1:
					print("MANY_PUNK_2\t" + src +'\t'+ trg)
					continue
			else:
				print("MANY_PUNK_2\t" + src +'\t'+ trg)
				continue
		if any([old in toks_1 for old in ['thou', 'thee', 'hast', 've']]) or any([old in toks_2 for old in ['thou', 'thee', 'hast', 've']]):
			print("old_english\t" + src +'\t'+ trg)
			continue
		if '_' in line:
			print("under_score\t" + src +'\t'+ trg)
			continue
		f_out.write(src +'\t'+ trg + '\n')
